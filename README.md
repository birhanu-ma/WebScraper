# WebScraper
## postgresSQL documentation
## Database Schema

### Tables

#### banks
| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| bank_id     | SERIAL | PRIMARY KEY | Unique bank identifier |
| bank_name   | VARCHAR(255) | NOT NULL | Official bank name |
| app_name    | VARCHAR(255) | NULLABLE | Bank app name |

#### reviews
| Column Name       | Type | Constraints | Description |
|------------------|------|-------------|-------------|
| review_id         | SERIAL | PRIMARY KEY | Unique review identifier |
| bank_id           | INT | NOT NULL, FK → banks(bank_id) | Associated bank |
| review_text       | TEXT | NULLABLE | Full review text |
| rating            | NUMERIC(2,1) | NULLABLE | User rating (1–5) |
| review_date       | DATE | NULLABLE | Review submission date |
| sentiment_label   | VARCHAR(20) | NULLABLE | NLP sentiment label |
| sentiment_score   | NUMERIC(3,2) | NULLABLE | Confidence score (0–1) |
| theme             | VARCHAR(50) | NULLABLE | Thematic category |
| source            | VARCHAR(50) | NULLABLE | Review source |

### Relationships
- One-to-Many: `banks.bank_id` → `reviews.bank_id`
- `ON DELETE CASCADE` ensures deleting a bank removes its reviews.
