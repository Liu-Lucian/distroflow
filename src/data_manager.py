"""Data export and management functionality"""

import pandas as pd
import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from .config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manage lead data and exports"""

    def __init__(self):
        self.exports_dir = Path(config.EXPORTS_DIR)
        self.exports_dir.mkdir(exist_ok=True)

    def export_to_csv(self, data: List[Dict], filename: str = None) -> str:
        """
        Export data to CSV

        Args:
            data: List of dictionaries
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        if not data:
            logger.warning("No data to export")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_{timestamp}.csv"

        filepath = self.exports_dir / filename

        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None

    def export_to_excel(self, data: List[Dict], filename: str = None) -> str:
        """
        Export data to Excel with formatting

        Args:
            data: List of dictionaries
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        if not data:
            logger.warning("No data to export")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_{timestamp}.xlsx"

        filepath = self.exports_dir / filename

        try:
            df = pd.DataFrame(data)

            # Create Excel writer with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Leads', index=False)

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Leads']

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None

    def export_to_json(self, data: List[Dict], filename: str = None) -> str:
        """
        Export data to JSON

        Args:
            data: List of dictionaries
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        if not data:
            logger.warning("No data to export")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_{timestamp}.json"

        filepath = self.exports_dir / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None

    def load_from_json(self, filepath: str) -> List[Dict]:
        """
        Load data from JSON file

        Args:
            filepath: Path to JSON file

        Returns:
            List of dictionaries
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading from JSON: {e}")
            return []

    def generate_report(self, leads: List[Dict]) -> Dict:
        """
        Generate summary statistics report

        Args:
            leads: List of lead dictionaries

        Returns:
            Report dictionary
        """
        if not leads:
            return {}

        df = pd.DataFrame(leads)

        report = {
            'total_leads': len(leads),
            'timestamp': datetime.now().isoformat(),
        }

        # Add follower statistics if available
        if 'followers_count' in df.columns:
            report['avg_followers'] = int(df['followers_count'].mean())
            report['max_followers'] = int(df['followers_count'].max())
            report['min_followers'] = int(df['followers_count'].min())

        # Count emails found
        if 'email' in df.columns:
            report['emails_found'] = df['email'].notna().sum()
            report['email_rate'] = f"{(report['emails_found'] / len(leads) * 100):.1f}%"

        # Count by source if available
        if 'found_via' in df.columns:
            report['sources'] = df['found_via'].value_counts().to_dict()

        return report

    def export_campaign_summary(
        self,
        leads: List[Dict],
        influencers: List[Dict],
        keywords_used: List[str],
        filename: str = None
    ) -> str:
        """
        Export a comprehensive campaign summary

        Args:
            leads: List of scraped leads
            influencers: List of influencers targeted
            keywords_used: Keywords used in search
            filename: Output filename

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"campaign_summary_{timestamp}.xlsx"

        filepath = self.exports_dir / filename

        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Leads sheet
                if leads:
                    df_leads = pd.DataFrame(leads)
                    df_leads.to_excel(writer, sheet_name='Leads', index=False)

                # Influencers sheet
                if influencers:
                    df_influencers = pd.DataFrame(influencers)
                    df_influencers.to_excel(writer, sheet_name='Influencers', index=False)

                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Leads',
                        'Total Influencers',
                        'Keywords Used',
                        'Campaign Date',
                        'Avg Follower Count',
                        'Emails Found'
                    ],
                    'Value': [
                        len(leads),
                        len(influencers),
                        ', '.join(keywords_used),
                        datetime.now().strftime("%Y-%m-%d %H:%M"),
                        int(pd.DataFrame(leads)['followers_count'].mean()) if leads and 'followers_count' in pd.DataFrame(leads).columns else 'N/A',
                        sum(1 for lead in leads if lead.get('email')) if leads else 0
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)

            logger.info(f"Exported campaign summary to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting campaign summary: {e}")
            return None


# Example usage
if __name__ == "__main__":
    manager = DataManager()

    # Sample data
    sample_leads = [
        {
            'username': 'johndoe',
            'name': 'John Doe',
            'email': 'john@example.com',
            'followers_count': 5000,
            'description': 'Tech enthusiast'
        },
        {
            'username': 'janedoe',
            'name': 'Jane Doe',
            'email': None,
            'followers_count': 3000,
            'description': 'Product Manager'
        }
    ]

    # Export to different formats
    csv_path = manager.export_to_csv(sample_leads)
    print(f"CSV exported to: {csv_path}")

    excel_path = manager.export_to_excel(sample_leads)
    print(f"Excel exported to: {excel_path}")

    # Generate report
    report = manager.generate_report(sample_leads)
    print(f"\nReport: {report}")
