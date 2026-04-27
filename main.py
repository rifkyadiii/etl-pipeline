import logging
from utils.extract import scrape_main
from utils.transform import transform_data
from utils.load import load_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Starting the ETL process...")

    # Extract
    logging.info("Starting the Extraction phase...")
    extracted_df = scrape_main()
    if extracted_df is not None and not extracted_df.empty:
        logging.info(f"Successfully extracted {len(extracted_df)} records.")

        # Transform
        logging.info("Starting the Transformation phase...")
        transformed_df = transform_data(extracted_df.copy())
        logging.info(f"Successfully transformed {len(transformed_df)} records.")

        # Load
        logging.info("Starting the Load phase...")
        load_successful = load_data(transformed_df.copy())
        if load_successful:
            logging.info("ETL process completed successfully!")
        else:
            logging.error("ETL process completed with some loading failures.")
    else:
        logging.error("No data extracted. ETL process aborted.")