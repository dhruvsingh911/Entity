from datasets import load_dataset

print("Dataset loading...")

ds = load_dataset("ankitdhiman/hinglish-conversations")

print(ds)

print("\nFirst conversation:")
print(ds["train"][0])
