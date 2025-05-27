from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
import pydantic
from pydantic import BaseModel,computed_field,Field
import json
from typing import Annotated,Literal

app = FastAPI()

def load_data():
  with open('patients.json', 'r') as f:
    data = json.load(f)
  return data

def save_data(data):
  with open("patients.json",'w') as f:
    json.dump(data,f)


@app.get("/")
def hello_world():
    return {"message": "Patient management system API"}
  
@app.get("/about")
def about():
  return {"message":"TA fully functional API to manage patients, doctors records."}

@app.get("/view")
def view():
  data = load_data()
  return data

#path parameter and HTTPException
@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(...,description="Id of the patient in the db",examples="P001")):
  data = load_data()
  if patient_id in data:
    return data[patient_id]
  raise HTTPException(status_code=404, detail="Patient not found") 


# Query parameter
@app.get('/sort')
def sort_data(sort_by:str = Query(...,description="sort on the basis of height, weight or bmi"),
              order:str=Query('asc',description="sort in asc or desc order")):
  valid_fields = ['height','weight','bmi']
  
  if sort_by not in valid_fields:
    raise HTTPException(status_code=400,detail=f"Invalid fields, select from {valid_fields}")
  
  if order not in ['asc','desc']:
    raise HTTPException(status_code=400,detail=f"Invalid order, select from asc or desc select from [asc,desc]")
  data = load_data()
  sort_order = True if order=='desc' else False
  sorted_data = sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)  
  return sorted_data

# create new patient record

# to create the new patient record we need to create the pydantic model to verify the valid data for new patient
class Patient(BaseModel):
  id:Annotated[str, Field(...,description="ID of the patient",examples=["P001"])]
  name:Annotated[str,Field(...,description="Name of the patient")]
  city:Annotated[str,Field(...,description='City')]
  age:Annotated[int,Field(...,gt=0,lt=120,description="age of the patient")]
  gender:Annotated[Literal['male','female','other'],Field(...,description="Gender of the patient")]
  height:Annotated[float,Field(...,gt=0,description="height of the patient in mts")]
  weight:Annotated[float,Field(...,gt=0,description="weight of the patient in kgs")]
  
  @computed_field
  @property
  def bmi(self)->float:
    bmi = round(self.weight/(self.height**2),2)
    return bmi
  @computed_field
  @property
  def verdict(self)->str:
    if self.bmi<18.5:
      return "underweight"
    elif self.bmi<25:
      return "Normal"
    elif self.bmi<30:
      return "Normal"
    else:
      return "Obese"
  

# Request body: it is the portion which requires the api to create thenew record

@app.post('/create')
def create_patient(patient:Patient):
  #load existing data
  data = load_data()

  #check if the patient already exisit
  if patient.id in data:
    raise HTTPException(status_code=400,detail="Patient already exist")

  #if new patient : will insert to db
  data[patient.id]=patient.model_dump(exclude=['id'])
  
  # save the file
  save_data(data)

  # response that user inserted
  return JSONResponse(status_code=201, content={"messsage":"patient created successfully"})

# delete the 
