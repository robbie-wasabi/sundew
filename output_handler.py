import json
import csv
import os
import logging
from datetime import datetime

class OutputHandler:
    def __init__(self, output_format, output_destination):
        self.output_format = output_format.lower()
        self.output_destination = output_destination
        self.ensure_output_directory()
        self.transformation_report = []
        logging.info(f"OutputHandler initialized with format: {output_format}, destination: {output_destination}")

    def ensure_output_directory(self):
        os.makedirs(os.path.dirname(self.output_destination), exist_ok=True)

    def save(self, data):
        try:
            if self.output_format == 'json':
                self.save_json(data)
            elif self.output_format == 'csv':
                self.save_csv(data)
            elif self.output_format == 'text':
                self.save_text(data)
            else:
                raise ValueError(f"Unsupported output format: {self.output_format}")
            
            self.save_transformation_report()
            logging.info(f"Data saved successfully to {self.output_destination}")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")
            self.log_error(str(e))

    def save_json(self, data):
        with open(self.output_destination, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.add_to_report(f"Saved {len(data)} items in JSON format")

    def save_csv(self, data):
        if not data:
            logging.warning("No data to save to CSV")
            self.add_to_report("No data to save to CSV")
            return
        
        with open(self.output_destination, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        self.add_to_report(f"Saved {len(data)} rows in CSV format")

    def save_text(self, data):
        with open(self.output_destination, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(str(item) + '\n')
        self.add_to_report(f"Saved {len(data)} lines in text format")

    def add_to_report(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transformation_report.append(f"[{timestamp}] {message}")

    def log_error(self, error_message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log_path = os.path.join(os.path.dirname(self.output_destination), "error_log.txt")
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] ERROR: {error_message}\n")

    def save_transformation_report(self):
        report_path = os.path.join(os.path.dirname(self.output_destination), "transformation_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            for entry in self.transformation_report:
                f.write(f"{entry}\n")
        logging.info(f"Transformation report saved to {report_path}")

    def record_transformation(self, original_data, transformed_data):
        """
        Record details about a specific transformation.
        """
        original_length = len(original_data) if isinstance(original_data, (list, dict)) else len(str(original_data))
        transformed_length = len(transformed_data) if isinstance(transformed_data, (list, dict)) else len(str(transformed_data))
        
        message = f"Transformed data: {original_length} characters -> {transformed_length} characters"
        self.add_to_report(message)

# Example usage:
# output_handler = OutputHandler('json', './output/transformed_data.json')
# output_handler.record_transformation(original_post, transformed_post)
# output_handler.save(all_transformed_posts)