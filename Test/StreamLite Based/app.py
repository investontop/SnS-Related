import streamlit as st

st.set_page_config(page_title="Streamlit Sample", page_icon=":snake:")

st.title("My first Streamlit app")
st.write("Choose an operation and enter two values.")

operation = st.selectbox(
	"Choose an operation",
	["Add", "Subtract", "Multiply", "Divide"],
)

first_value = st.number_input("First value", value=0.0)
second_value = st.number_input("Second value", value=0.0)

if st.button("Calculate"):
	if operation == "Add":
		result = first_value + second_value
	elif operation == "Subtract":
		result = first_value - second_value
	elif operation == "Multiply":
		result = first_value * second_value
	elif second_value == 0:
		st.error("You cannot divide by zero.")
		st.stop()
	else:
		result = first_value / second_value

	st.success(f"Result: {result}")

