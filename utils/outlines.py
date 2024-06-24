# # login to access mistral model
# from huggingface_hub import login
# login()

# Multiple choices

# You can reduce the completion to a choice between multiple possibilities:

# import outlines

# model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

# prompt = """You are a sentiment-labelling assistant.
# Is the following review positive or negative?

# Review: This restaurant is just awesome!
# """

# generator = outlines.generate.choice(model, ["Positive", "Negative"])
# answer = generator(prompt)

# Type constraint

# You can instruct the model to only return integers or floats:

# import outlines

# model = outlines.models.transformers("WizardLM/WizardMath-7B-V1.1")

# prompt = "<s>result of 9 + 9 = 18</s><s>result of 1 + 2 = "
# answer = outlines.generate.format(model, int)(prompt)
# print(answer)
# # 3

# prompt = "sqrt(2)="
# generator = outlines.generate.format(model, float)
# answer = generator(prompt, max_tokens=10)
# print(answer)
# # 1.41421356

# Efficient regex-structured generation

# Outlines also comes with fast regex-structured generation. In fact, the choice and format functions above all use regex-structured generation under the hood:

# import outlines

# model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

# prompt = "What is the IP address of the Google DNS servers? "

# generator = outlines.generate.text(model)
# unstructured = generator(prompt, max_tokens=30)

# generator = outlines.generate.regex(
#     model,
#     r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)",
# )
# structured = generator(prompt, max_tokens=30)

# print(unstructured)
# # What is the IP address of the Google DNS servers?
# #
# # Passive DNS servers are at DNS servers that are private.
# # In other words, both IP servers are private. The database
# # does not contain Chelsea Manning

# print(structured)
# # What is the IP address of the Google DNS servers?
# # 2.2.6.1

# Unlike other libraries, regex-structured generation in Outlines is almost as fast as non-structured generation.
# Efficient JSON generation following a Pydantic model

# Outlines 〰 allows to guide the generation process so the output is guaranteed to follow a JSON schema or Pydantic model:

# from enum import Enum
# from pydantic import BaseModel, constr

# import outlines
# import torch


# class Weapon(str, Enum):
#     sword = "sword"
#     axe = "axe"
#     mace = "mace"
#     spear = "spear"
#     bow = "bow"
#     crossbow = "crossbow"


# class Armor(str, Enum):
#     leather = "leather"
#     chainmail = "chainmail"
#     plate = "plate"


# class Character(BaseModel):
#     name: constr(max_length=10)
#     age: int
#     armor: Armor
#     weapon: Weapon
#     strength: int


# model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.2")

# # Construct structured sequence generator
# generator = outlines.generate.json(model, Character)

# # Draw a sample
# rng = torch.Generator(device="cuda")
# rng.manual_seed(789001)

# character = generator("Give me a character description", rng=rng)

# print(repr(character))
# # Character(name='Anderson', age=28, armor=<Armor.chainmail: 'chainmail'>, weapon=<Weapon.sword: 'sword'>, strength=8)

# character = generator("Give me an interesting character description", rng=rng)

# print(repr(character))
# # Character(name='Vivian Thr', age=44, armor=<Armor.plate: 'plate'>, weapon=<Weapon.crossbow: 'crossbow'>, strength=125)

