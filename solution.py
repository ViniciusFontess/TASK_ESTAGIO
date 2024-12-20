from flask import Flask, render_template, redirect, request
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'

# Para funcionamento do código, **É DE EXTREMA IMPORTÂNCIA COLOCAR** patentes.html numa pasta chamada templates, para o funcionamento do flask!!!!

@app.route('/')
def all_patentes():
    
    # Obtém a lista de arquivos HTML no diretório 'problems', pasta criada para colocar os 10 htmls do problema e ordená-los para facilidade
    # Para funcionar é necessário colocar os 10 htmls na pasta 'problems'

    template_files = sorted([f for f in os.listdir('problems') if f.endswith('.html')])
    patentes = []
    # Lista de resultados predefinidos dos 10 htmls
    resultados = [2, 0, 0, 0, 0, 0, 3, 0, 0, 41]

    # Itera sobre os primeiros 10 arquivos de template
    for i, template_file in enumerate(template_files[:10]):
        # Extrai o nome do arquivo
        patente_id = template_file.replace('.html', '')
        # Extrai o CNPJ 
        cnpj = patente_id.split('-')[0]
        # Obtém o resultado correspondente ao índice atual
        resultado = resultados[i]
        
        file_path = os.path.join('problems', template_file)
        try:
            # Tenta abrir e ler o conteúdo do arquivo HTML
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        except UnicodeDecodeError as e:
            # Em caso de erro de decodificação, imprime o erro e continua
            print(f"Error reading {file_path}: {e}")
            continue

        # Usa BeautifulSoup(biblioteca importante) para analisar o conteúdo HTML
        soup = BeautifulSoup(content, 'html.parser')
        # Extrai textos de elementos com a classe 'visitado'
        numbers = [element.get_text(strip=True) for element in soup.find_all(class_='visitado')]
        # Extrai textos de elementos com a classe 'deposito'
        deposit_dates = [element.get_text(strip=True) for element in soup.find_all(class_='deposito')]
        # Extrai textos de elementos com a classe 'titulos'
        titles = [element.get_text(strip=True) for element in soup.find_all(class_='titulos')]
        # Extrai textos de elementos com a classe 'alerta'
        alerts = [element.get_text(strip=True) for element in soup.find_all(class_='alerta')]

        if resultado > 1: 
            # Se o resultado for maior que 1, itera e adiciona múltiplas entradas
            # Para os casos de resultado maior que 1, para ficar um em baixo do outro
            for j in range(1, resultado + 1):
                number = numbers[j-1] if j-1 < len(numbers) else ''
                deposit_date = deposit_dates[j-1] if j-1 < len(deposit_dates) else ''
                title = titles[j-1] if j-1 < len(titles) else ''
                alert = alerts[j-1] if j-1 < len(alerts) else ''
                patentes.append({'name': patente_id, 'cnpj': cnpj, 'resultado': j, 'number': number, 'deposit_date': deposit_date, 'title': title, 'alert': alert})
        else:
            # Se o resultado for 1 ou menos, adiciona uma única entrada
            number = numbers[0] if numbers else ''
            deposit_date = deposit_dates[0] if deposit_dates else ''
            title = titles[0] if titles else ''
            alert = alerts[0] if alerts else ''
            patentes.append({'name': patente_id, 'cnpj': cnpj, 'resultado': resultado, 'number': number, 'deposit_date': deposit_date, 'title': title, 'alert': alert})

    # Renderiza o template 'patentes.html' com a lista de patentes
    return render_template('patentes.html', patentes=patentes)

if __name__ == '__main__':
    app.run(debug=True)

#No ultimo html, o resultado é 41, porém passando do resultado 20 a página não consegue ser carregada no próprio HTML e não possui os respectivos Números de Pedido, Data de Depósito, Título e IPC, então eles não são exibidos na página.