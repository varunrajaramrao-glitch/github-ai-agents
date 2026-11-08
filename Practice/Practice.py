from fastapi import FastAPI
app= FastAPI()
@app.post("/practice")
async def practice_program(user_input: str):
    return {"message": f"Hello, {user_input}! This is a practice program."}