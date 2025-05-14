import hashlib
import streamlit as st
from cryptography.fernet import Fernet
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import base64

load_dotenv()
supabase_url = st.secrets("SUPABASE_URL")
supabase_key = st.secrets("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

st.title("🏠 Secure Data encryption")


def main():
    MASTER_KEY = st.secrets("MASTER_KEY")
    KEY = base64.urlsafe_b64encode(hashlib.sha256(MASTER_KEY.encode()).digest())
    cipher = Fernet(KEY)

    if "failed_attempts" not in st.session_state:
        st.session_state.failed_attempts = 0

    def hash_passkey(passkey: str) -> str:
        return hashlib.sha256(passkey.encode()).hexdigest()

    def encrypt_data(text: str):
        return cipher.encrypt(text.encode()).decode()

    def retrieve_data(data_id: str):
        try:
            data = supabase.table("users_data").select("*").eq("id", data_id).execute()
            if data.data:
                return data.data[0]
            else:
                return None
        except Exception as e:
            st.error(f"Failed to retrieve data from database: {e}")
            return None

    def decrypt_data(encrypted_data: str):
        try:
            return cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            st.error(f"Decryption failed: {e}")
            return None

    def verify_passkey(stored_hash: str, provided_passkey: str) -> bool:
        hashed_provided = hash_passkey(passkey=provided_passkey)
        return hashed_provided == stored_hash

    menu = ["Home", "Retrieve Data"]
    options = st.sidebar.selectbox("Navigation", menu)

    if options == "Home":
        st.write(
            "Enter your data below and set passkey, you will then get a unique id, keep it safe as you can **NOT** decrypt your data without it"
        )
        user_data = st.text_area("Enter your data")
        user_passkey = st.text_input("Set Passkey", type="password")

        if st.button("Encrypt and Save"):
            if user_data and user_passkey:
                hashed_passkey = hash_passkey(passkey=user_passkey)
                encrypted_data = encrypt_data(text=user_data)
                try:
                    stored_data = (
                        supabase.table("users_data")
                        .insert(
                            {
                                "user_data": encrypted_data,
                                "user_passkey": hashed_passkey,
                            }
                        )
                        .execute()
                    )
                    data_id = stored_data.data[0]["id"]
                    st.success(f"Your data is stored successfully")
                    st.code(data_id)
                except Exception as e:
                    st.error(f"Failed to store data into database: {e}")
            else:
                st.error("Why so hurry 🤨? Fill out the data first")

    elif options == "Retrieve Data":
        st.subheader("Retrieve Your Data 😉")
        data_id = st.text_input("Enter Your data id")
        user_passkey = st.text_input("Enter Your passkey", type="password")

        if st.button("Retrieve Data"):
            if data_id and user_passkey:
                data = retrieve_data(data_id=data_id)
                if data:
                    if verify_passkey(data["user_passkey"], user_passkey):
                        st.session_state.failed_attempts = 0
                        decrypted_data = decrypt_data(encrypted_data=data["user_data"])
                        if decrypted_data:
                            st.success("Data retrieved successfully")
                            st.write(decrypted_data)
                        else:
                            st.error("Failed to decrypt data")
                    else:
                        st.session_state.failed_attempts += 1
                        st.error(
                            f"Incorrect passkey {st.session_state.failed_attempts} / 3"
                        )

                        if st.session_state.failed_attempts >= 3:
                            st.error("Too many failed attempts. Try again later")
                            st.session_state.failed_attempts = 0
                            st.rerun()
                else:
                    st.error("Data not found")
            else:
                st.error("Why so hurry 🤨? Fill out the data id and passkey first")


if __name__ == "__main__":
    main()
