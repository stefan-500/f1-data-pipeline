from kafka import KafkaProducer, KafkaConsumer
from database.init_db import engine
from models.metadata import Race, _Time, QualificationDate
from sqlalchemy import insert, select
from sqlalchemy.orm import Session
import json
import numpy as np
import requests
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def produce_quali_dates():

    producer = KafkaProducer(
        bootstrap_servers='broker:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    seasons = np.arange(2012, 2026)
    records = []

    for season in seasons:
        url = f"https://api.jolpi.ca/ergast/f1/{season}/races/"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            
            # Parse qualifying date
            for race in data["MRData"]["RaceTable"]["Races"]:

                quali = race.get("Qualifying", {})
                quali_date = quali.get("date")

                record = {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "quali_date": quali_date,
                    # Add quali_date_id, an integer representation of quali_date
                    "quali_date_id": int(datetime.strptime(quali_date, "%Y-%m-%d").strftime("%Y%m%d")) if quali_date else None
                }

                records.append(record)
                producer.send("f1_race_qualifications_api", value=record)

        else:
            logging.debug(f"Failed to retrieve data:", {response.status_code})

    producer.flush()
    producer.close()

    print("All messages sent!")

def consume_and_insert_quali():

    consumer = KafkaConsumer(
        'f1_race_qualifications_api',
        bootstrap_servers='broker:29092',
        auto_offset_reset='earliest',
        group_id='f1_consumers',
        enable_auto_commit=True,
        consumer_timeout_ms=10_000, # stop if no messages for 10s
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    valid_keys = {'quali_date_id', 'race_id', 'quali_date'}
    batch = []
    batch_size = 15

    with Session(engine) as session:
        try:
            for message in consumer:
                row = message.value

                # Ensure types
                try:
                    season_str = str(row.get('season'))
                    round_val = int(row.get('round')) if row.get('round') is not None else None
                except Exception:
                    logging.warning(f"Invalid season/round in message, skipping: {row}")
                    continue

                # Link Qualifying with Race by season(time_year) and round
                race = session.execute(
                    select(Race).join(_Time, Race.time_id == _Time.time_id)
                    .where(_Time.time_year == season_str)
                    .where(Race.round == round_val)
                ).scalar_one_or_none()

                if not race:
                    logging.warning(f"No matching race for year {season_str} round {round_val}.")
                    continue
                    
                # Prepare dict with race_id and allowed keys
                row['race_id'] = race.race_id
                insert_row = {k: row[k] for k in valid_keys if k in row}
                batch.append(insert_row)

                if len(batch) >= batch_size:
                    try:
                        session.execute(insert(QualificationDate), batch)
                        session.commit()
                        batch.clear()
                    except IntegrityError as ie:
                        session.rollback()
                        logging.warning("Batch insert IntegrityError, falling back to single-row inserts.")

                        for r in batch:
                            try:
                                session.execute(insert(QualificationDate).values(r))
                                session.commit()
                            except IntegrityError:
                                session.rollback()
                                logging.info(f"Skipping bad row: {r}")
                        batch.clear()
            
            # Insert remaining batch
            if batch:
                try:
                    session.execute(insert(QualificationDate), batch)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    for r in batch:
                        try:
                            session.execute(insert(QualificationDate).values(r))
                            session.commit()
                        except IntegrityError:
                            session.rollback()
                            logging.info(f"Skipping duplicate or bad row: {r}")

            logging.info("Qualification Date - Success!")

        except Exception as e:
            session.rollback()
            logging.error("Error while consuming and inserting Qualification Dates.", e)
            raise
        
        finally:
            consumer.close()