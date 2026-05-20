import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("customer_care_docs")
results = collection.get()
print("Total docs:", len(results["ids"]))
if len(results["ids"]) > 0:
    print("Sample metadata:", results["metadatas"][0])
    print("Sample doc:", results["documents"][0][:100])
