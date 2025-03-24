# Forms-fields system API

backend service built with FastAPI, pydantic validations, pytest unit testing, SQLAlchemy as ORM with PostgreSQL.

## Features

- Create and manage forms with multiple fields
- Reference fields across different forms, handling of hierarchical form-field relationships
- Submit and retrieve form responses
- taking code quality into consideration Cognitive-complexity score < 15
- class-based logging, try/except graceful exception handling
- extensible, modular approach, test case validations

## Technical Implementation

## Database Design
### Reference fields across formss and thus a many-to-many relationship between forms and fields, along with a self-referential relationship in the Field model.
The database design is centered around four main models:

1. **Form**: Represents a collection of fields
2. **Field**: Represents a single field with type information
3. **Submission**: Represents a filled form
4. **FieldValue**: Stores the actual values submitted for each field \
    ![image](https://github.com/user-attachments/assets/5f2654ad-f5f9-4ba0-911b-1dd0d0d02f26)




### Further:
. **Database Indexing**: All foreign keys and frequently queried columns are indexed, and joined load from sqlalchemy \
. **Pagination**: All list endpoints support pagination to limit response size \
. JSON column type for field values to avoid complex joins \
. Tested with both local postgress and serverless neon db postgress

## Setup Instructions



1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
![image](https://github.com/user-attachments/assets/3b7a1860-8939-4b8d-95e8-3d86667a9950) 
**supports unified PostgreSQL connection URL
or change the docker implementation as per need:**

![image](https://github.com/user-attachments/assets/9856f943-9b1a-4340-9617-18e563d5c10b)


2. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

   or locally
   ```bash
    uvicorn app.main:app --reload
   ```

4. The API will be available as per your set port mapping 


## API Documentation

Once the API is running, you can view the interactive API documentation at fastapi's swagger openapi page

## Testing

Run the tests with pytest in the same directory:

```bash
python -m pytest
```

To run with coverage report:

```bash
pytest --cov=app
```

## Assumptions and Technical Decisions

1.  Fields can be referenced across forms, and these referenced fields can be edited from both forms; Maintaining data integrity, the actual data is stored only once, and references are maintained through relationships.

2. supporting multi-tenancy by not having any global fields, Each field is either owned by a form or references another field, sharing the relationship

3. **Field Types**: The system supports different field types text, number, date, etc.... through a field_type attribute and JSON storage for values.

4. **API Design**: RESTful API principles have been followed, with clear resource paths and HTTP methods that match the operations.

5. **Error Handling**: Comprehensive error handling with appropriate HTTP status codes and error messages, elaboarative class based logging

6. The design prioritizes GET operations for form submissions, as they are expected to be 1000x more frequent than POST operations.
7. SQL Alchemy as ORM
8. Asynchronous database schema creation

### Potential Features can be added:
1. Redis caching for all GET endpoints, handling cache invalidation for POST/PUT/DELETE Operations (FastAPICache.clear)
2. elaborative documentation on swagger page and as postman profile
3. CDN like cloudinary can be integrated for media possibilities, media fields and object storage with MinIO, amazon s3
4. More reduced redundant queries by using joins
5. Integration testing, observability
6. Frontend fullstack app for the SAAS tool
