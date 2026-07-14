<img width="1920" height="1080" alt="main" src="https://github.com/user-attachments/assets/e0ec8970-5cae-4c30-8b93-c01d675d0af1" />


thats what the project should look like while being used (i know i am bad in blender and thats a projector) so what sould this project will do?
and how does it work?

this project start with the idea of being able to play games by moving its like vr but not like it 
# how to use it?
first we start by having a projector that project what else can it do you should be wearing the projector cause
i didnt want to use another esp and an expensive motor to move the projector from the ceiling soo to use this you should buy a small projector

now we have the mapper(or render in my photo) in the start you should connect it to the computer then you should map the whole room(better if the room is rectangular) you let it map and try to not get
in its way it will have a 3 sec cool down every time so you can move away it take like 12 sec or less

after mapping it becomes easy just open your game wear the headset and turn it on then connect the headset to the computer and run the python code(it will be the one who moves you in game)

# what will every part do?
i think i said that the mapping will map the room so we get your position and its easy using an ultrasonic sensor

<img width="696" height="508" alt="لقطة شاشة 2026-07-14 194043" src="https://github.com/user-attachments/assets/a1f995d4-fa7a-47a0-8bfb-87ab0c2551ad" />


the headset: it has an MPU6050 it will detect where you look so it moves it in game

and it have two ultrasonic sensors that detects where you are using how far you are forward and right so we can see where you move usin that

<img width="774" height="476" alt="لقطة شاشة 2026-07-14 181825" src="https://github.com/user-attachments/assets/ce92c6c3-e0ff-4479-abc7-aff3d0bdd589" />


and the python code will recive the room dimensions map it and now it gets your position and where you are looking and now it can move you in game
to move you it will use the libraries mouse and keyboard

# more about the project
-you can adjust the sesitivity so it matches the ingame 
-you can choose what the buttons do
# ---------
the designs i provided aren't the final to see the final check the journal 
