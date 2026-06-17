# backend/scripts/test_retrieval.py
from backend.app.services.vector_store import load_vector_store

def main():
    print("Loading local Chroma database...")
    # This connects to the database 
    vs = load_vector_store()

    # The question to ask the AI
    query = "What should I do for a sore throat?"
    print(f"\nSearching for: '{query}'\n")

    # similarity_search does the heavy lifting, pulling the top 3 closest matches
    results = vs.similarity_search(query, k=3)

    if not results:
        print("No results found. Did the database build correctly?")
        return

    # Print the results cleanly
    for i, doc in enumerate(results, 1):
        title = doc.metadata.get("title", "Unknown Title")
        chunk_id = doc.metadata.get("chunk_id", "No ID")
        
        print(f"--- MATCH {i} | Source: {title} ({chunk_id}) ---")
        print(doc.page_content.strip())
        print("-" * 60 + "\n")

if __name__ == "__main__":
    main()