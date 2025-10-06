echo "Instalando dependências do Analisador de Texto..."
pip install -r requirements.txt
python -m textblob.download_corpora
echo "Instalação concluída! Execute com: streamlit run app.py"
