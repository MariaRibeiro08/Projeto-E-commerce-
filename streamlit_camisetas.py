import streamlit as st
from controllers.camiseta_controller import CamisetaController

# Inicializar o controller apenas uma vez
if "controller" not in st.session_state:
    st.session_state.controller = CamisetaController()

controller = st.session_state.controller

st.title("CRUD de Camisetas (Streamlit)")


# Criar nova camiseta
st.subheader("Adicionar Camiseta")
tamanho = st.text_input("Tamanho:")
cor = st.text_input("Cor:")
preco = st.number_input("Preço:", min_value=0.0, step=0.01)

if st.button("Salvar"):
    if tamanho and cor and preco > 0:
        controller.criar(tamanho, cor, preco)
        st.success("Camiseta cadastrada com sucesso!")
    else:
        st.warning("Preencha todos os campos corretamente.")

# Listar camisetas
st.subheader("Camisetas cadastradas")
camisetas = controller.listar()

if camisetas:
    for c in camisetas:
        with st.expander(f"ID {c['id']} - {c['tamanho']} - {c['cor']} (R$ {c['preco']})"):
            novo_tamanho = st.text_input("Novo tamanho:", value=c["tamanho"], key=f"tamanho_{c['id']}")
            nova_cor = st.text_input("Nova cor:", value=c["cor"], key=f"cor_{c['id']}")
            novo_preco = st.number_input("Novo preço:", value=float(c["preco"]), key=f"preco_{c['id']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Atualizar", key=f"update_{c['id']}"):
                    controller.atualizar(c["id"], novo_tamanho, nova_cor, novo_preco)
                    st.success("Camiseta atualizada!")

            with col2:
                if st.button("Deletar", key=f"delete_{c['id']}"):
                    controller.deletar(c["id"])
                    st.success("Camiseta deletada!")
else:
    st.info("Nenhuma camiseta cadastrada ainda.")
