import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def auth():
    def sign_up(user_name: str, email: str, password: str):
        try:
            user = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"name": user_name}},
                }
            )
            return user
        except Exception as e:
            st.error(f"Registration Failed {e}")

    def sign_in(email: str, password: str):
        try:
            user = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            return user
        except Exception as e:
            st.error(f"Login Failed {e}")

    def auth_screen():
        st.title("Secure Data Encryption")
        st.write("Please login or sign up to continue")

        option = st.selectbox("Choose", ["Sign In", "Sign Up"])

        if option == "Sign In":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Sign In"):
                user = sign_in(email=email, password=password)
                if user and user.user:
                    st.session_state.user_email = user.user.email
                    # st.session_state.user_name = user.options.data.name
                    st.success(f"Welcome {email}")
                    st.rerun()

        elif option == "Sign Up":
            user_name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Sign Up"):
                user = sign_up(user_name=user_name, email=email, password=password)
                if user and user.user:
                    st.success("Successful 🥳! Please Sign In")

    auth_screen()


def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout Failed {e}")
