from rl_api import app
import env
import uvicorn
 

if __name__ == '__main__':
    print(env.HOST)
    print(env.PORT)
    uvicorn.run(app=app, host=env.HOST, port=env.PORT)
