import asyncio
from cost import *
import streamlit as st
from loguru import logger
from random import shuffle
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():

    # Main layout
    st.set_page_config(
        page_title="Strawberry Chat",
        page_icon="🍓"
    )

    with st.sidebar:
        if st.button("Clear chat history"):
            st.session_state.LOG = []
            st.rerun()
        model = st.radio(
            "**Model**",
            ["o1-mini", "o1-preview"],
            index=0
        )
        st.markdown("""<small><b>Stats</b><br>Page views <img src="https://www.cutercounter.com/hits.php?id=hvvxqdkqx&nd=5&style=1" border="0" alt="visitor counter"><br>Unique visitors <img src="https://www.cutercounter.com/hits.php?id=hmxqdkpc&nd=5&style=1" border="0" alt="website counter"></small>""", unsafe_allow_html=True)


    st.title('🍓 Strawberry Chat')
    st.caption(f"Currently using model: `{model}`. You can change the setting on the left 👈 sidebar.")
    conversation_container = st.container()

    # App logic

    if "LOG" not in st.session_state:
        st.session_state.LOG = []
        st.session_state.cost = 0

    if st.session_state.cost > 0:
        with st.sidebar:
            if st.session_state.cost < 0.01:
                cost_str = f"{st.session_state.cost:.3f}"
            else:
                cost_str = f"{st.session_state.cost:.2f}"
            st.info(f"Total cost for this session so far: USD $**{cost_str}**", icon="💲")
            st.caption("**This is a free preview by [Xiaopan.AI](https://xiaopan.ai)**.")
        if st.session_state.cost > 0.5:
            st.info(f"Total cost for this session so far: USD $**{cost_str}**", icon="💲")
            st.caption("**This is a free preview by [Xiaopan.AI](https://xiaopan.ai)**.")
            st.caption("If you find it useful and want to support me, you can scan below QR codes to help buy me a coffee ☕ or visit my portfolio (linked above) to check I can help you with anything.\n\nThank you! 🙏")
            
            # Render payment_images contents in random order
            payment_columns = st.columns(len(payment_images), gap="large", vertical_alignment="center")
            shuffle(payment_images)
            for i, image_path in enumerate(payment_images):
                with payment_columns[i]:
                    st.image(image_path, use_column_width=True)

    with conversation_container:
        # Render chat history so far in chat dialog
        for message in st.session_state.LOG:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Say something...")

    if prompt:

        with conversation_container:
            # Visualize user prompt
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                reply_box = st.empty()

        # Create a "pending" response visualization while waiting for the model to respond
        with reply_box:
            with st.spinner("Thinking..."):
                response = await client.chat.completions.create(
                    messages = st.session_state.LOG + [{"role": "user", "content": prompt}],
                    model = model,
                    stream = False,
                )

            logger.debug(response)
            
            message = response.choices[0].message
            if message.refusal:
                st.error(message.refusal)
            else:
                st.session_state.LOG.extend(
                    [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": message.content}
                    ]
                )
                st.markdown(message.content)

        # Count the cost
        usage = response.usage
        query_cost = cost[model]["prompt"] * usage.prompt_tokens + cost[model]["completion"] * usage.completion_tokens
        st.session_state.cost += query_cost

        st.rerun()

if __name__ == '__main__':
    asyncio.run(main())
