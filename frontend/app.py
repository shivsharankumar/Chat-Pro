import json
from typing import List

import requests
import streamlit as st

st.set_page_config(page_title="Doc Extractor", layout="wide")

st.title("Document Text Extractor")

with st.sidebar:
	st.header("Settings")
	api_url = st.text_input("API base URL", value="http://localhost:8000", help="FastAPI backend base URL")
	st.markdown("Use the uploader below to send files to the backend and extract their text.")

uploaded_files = st.file_uploader(
	"Upload PDFs or images",
	type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp"],
	accept_multiple_files=True,
)

if uploaded_files:
	if st.button("Extract text from all files"):
		results: List[dict] = []
		progress = st.progress(0)
		for idx, f in enumerate(uploaded_files, start=1):
			files = {"file": (f.name, f.getvalue(), f.type or "application/octet-stream")}
			try:
				resp = requests.post(f"{api_url}/extract", files=files, timeout=120)
				resp.raise_for_status()
				results.append(resp.json())
			except Exception as exc:
				results.append({
					"filename": f.name,
					"file_type": f.type,
					"method": f"error: {exc}",
					"num_pages": None,
					"text": "",
				})
			progress.progress(idx / len(uploaded_files))
		progress.empty()

		st.subheader("Results")
		for res in results:
			with st.expander(f"{res.get('filename')} — {res.get('method')}"):
				st.write(f"File type: {res.get('file_type')}")
				if res.get("num_pages") is not None:
					st.write(f"Pages: {res.get('num_pages')}")
				
				# Check if structured medical data is available
				structured_data = res.get("structured_data")
				if structured_data and structured_data.get("is_medical_document"):
					st.subheader("🏥 Medical Information")
					
					# Create columns for better layout
					col1, col2 = st.columns(2)
					
					with col1:
						if structured_data.get("name"):
							st.write(f"**Name:** {structured_data['name']}")
						if structured_data.get("age"):
							st.write(f"**Age:** {structured_data['age']}")
						if structured_data.get("allergies"):
							st.write(f"**Allergies:** {structured_data['allergies']}")
						if structured_data.get("medications"):
							st.write(f"**Medications:** {structured_data['medications']}")
					
					with col2:
						if structured_data.get("surgeries"):
							st.write(f"**Surgeries:** {structured_data['surgeries']}")
						if structured_data.get("history"):
							st.write(f"**History:** {structured_data['history']}")
						if structured_data.get("notes"):
							st.write(f"**Notes:** {structured_data['notes']}")
					
					st.divider()
				
				st.subheader("Raw Text")
				st.text_area("Extracted text", value=res.get("text") or "", height=260)
				
				col1, col2 = st.columns(2)
				with col1:
					st.download_button(
						"Download .txt",
						data=(res.get("text") or "").encode("utf-8"),
						file_name=(res.get("filename") or "extracted").rsplit(".", 1)[0] + ".txt",
						mime="text/plain",
					)
				with col2:
					st.download_button(
						"Download .json",
						data=json.dumps(res, ensure_ascii=False, indent=2).encode("utf-8"),
						file_name=(res.get("filename") or "extracted").rsplit(".", 1)[0] + ".json",
						mime="application/json",
					)
else:
	st.info("Upload one or more files to begin.")
