import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.dbModel import Base
from app.main import app
from app.db.database import getDb
from tests.testingData import addTestData, clearData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker





SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the fixture here in this file
@pytest.fixture(scope="function")
def db():
    """Initialize test db before each test"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)




def overrideTestDB():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[getDb] = overrideTestDB
client = TestClient(app)
# using fastapi testing client and pytest assertion

class TestFormsAPI:
    

    def test_createForm(self, db: Session):
        """Test creating a new form"""
        # Clear any existing data
        clearData(db)
        
        # Prepare test data
        formData = {
            "name": "Form testing T",
            "fields": [
                {"name": "Test Field ABC", "type": "number", "required": True},
                {"name": "XYZ 123", "type": "text", "required": True},
                {"name": "TESTER", "type": "text", "required": False},
            ]
        }
        
      
        response = client.post("/forms", json=formData)
        
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Form testing T"
        assert len(data["fields"]) == 3
        assert data["fields"][0]["name"] == "Test Field ABC"
        assert data["fields"][1]["name"] == "XYZ 123"

    def testGetForm(self, db: Session):
       
   
        clearData(db)
        
   
        test_data = addTestData(db)
        form_id = test_data["form1"].id
        

        response = client.get(f"/forms/{form_id}")
        
  
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Form 1"
        assert len(data["fields"]) == 3

    def test_Update(self, db: Session):
        """Test updating a form"""
        # Clear any existing data
        clearData(db)
        
        # Create test data
        testData = addTestData(db)
        formId = testData["form1"].id
        
        # Prepare update data
        updateData = {
            "name": "New Test Form 1",
            "fields_add": [
                {"name": "New Field update", "type": "text", "required": True}
            ],
            "fields_remove": [],
            "fields_update": {}
        }
        
        # Make request
        response = client.put(f"/forms/{formId}", json=updateData)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Test Form 1"
        assert len(data["fields"]) == 4  # Original 3 + 1 new

    def test_fieldLinking(self, db: Session):
        """Test field linking in two forms"""
        # referencing
        clearData(db)
        
        # Create test data
        testData = addTestData(db)
        form1Id = testData["form1"].id
        form2Id = testData["form2"].id
        field2Id = testData["field2"].id
        field2RefId = testData["field2_ref"].id
        
        # Get form 2
        response = client.get(f"/forms/{form2Id}")
        assert response.status_code == 200
        form2Data = response.json()
        
        # Find the referenced field
        referencedField = None
        for field in form2Data["fields"]:
            if field["name"] == "Referenced Field 2":
                referencedField = field
                break
        
        assert referencedField is not None
        assert referencedField["refer_field_id"] == field2Id
        
        # Create a submission for form 1 with a new value for field 2
        submissionData = {
            "form_id": form1Id,
            "field_values": [
                {"field_id": field2Id, "value": "Updated with Ist Form"}
            ]
        }
        
        response = client.post(f"/forms/{form1Id}/submissions", json=submissionData)
        assert response.status_code == 201
        
        # Create a submission for form 2 with the referenced field
        submissionData = {
            "form_id": form2Id,
            "field_values": [
                {"field_id": field2RefId, "value": "Updated with IInd Form"}
            ]
        }
        
        response = client.post(f"/forms/{form2Id}/submissions", json=submissionData)
        assert response.status_code == 201
        
       

    def test_getSubmission(self, db: Session):
        """Test get submission"""
       
        clearData(db)
        
        # test dataa
        testData = addTestData(db)
        formId = testData["form1"].id
        submissionId = testData["submission1"].id
        
       
        response = client.get(f"/forms/{formId}/submissions/{submissionId}")
        
    
        assert response.status_code == 200
        data = response.json()
        assert data["form_id"] == formId
        assert data["id"] == submissionId
        assert "Field 1" in data["values"]
        assert "Field 2" in data["values"]
        assert "Field 3" in data["values"]
        assert data["values"]["Field 1"] == "Sample Text for Field 1"
        assert data["values"]["Field 2"] == "Sample Text for Field 2"
        assert data["values"]["Field 3"] == 42