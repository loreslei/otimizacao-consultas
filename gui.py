import tkinter as tk
from tkinter import scrolledtext, messagebox
import traceback
import os
from parser import tokenize, parse_multiplas_queries as parse, validar_schema, gerar_grafo_networkx,gerar_algebra_relacional
from data import bd
from pyvis.network import Network
import json


def gerar_grafos_html(lista_de_queries, bd):
    """
    Generate HTML graphs for each query in the list.
    
    Args:
        lista_de_queries: List of parsed query objects
        bd: Database schema information
        
    Returns:
        List of generated HTML file paths
    """
    arquivos_gerados = []
    
    for idx, query_data in enumerate(lista_de_queries):
        try:
            # Generate networkx graph
            G,plano = gerar_grafo_networkx(query_data, bd)
            
            for i, passo in enumerate(plano, 1):
                  print(f"{i}. {passo}")

            # Configure node styling
            for node in G.nodes():
                G.nodes[node]['shape'] = 'box'
                G.nodes[node]['color'] = {
                    'background': '#dbeafe', 
                    'border': '#38bdf8',
                }
                
                G.nodes[node]['font'] = {'size': 16, 'face': 'Segoe UI', 'multi': 'html'}
                texto_atual = G.nodes[node].get('label', str(node))
                G.nodes[node]['label'] = f"<b>{texto_atual}"
                G.nodes[node]['widthConstraint'] = {'minimum': 160}
                G.nodes[node]['heightConstraint'] = {'minimum': 60}
                G.nodes[node]['margin'] = 15 
                G.nodes[node]['borderWidth'] = 2
            
            # Create visualization
            net = Network(height="800px", width="100%", directed=True)
            net.from_nx(G)
            
            net.set_options("""
            var options = {
            "interaction": {
                "selectable": false,
                "dragNodes": false,
                "dragView": true,
                "zoomView": true
            },              
            "edges": {
                "smooth": {
                "type": "cubicBezier",
                "forceDirection": "vertical",
                "roundness": 0.4
                }
            },
            "layout": {
                "hierarchical": {
                "enabled": true,
                "direction": "DU",
                "sortMethod": "directed",
                "levelSeparation": 200,
                "nodeSpacing": 300
                }
            },
            "physics": {
                "enabled": false
            }
            }
            """)
            
            # Save HTML file
            ficheiro_saida = f"grafo_query_{idx + 1}.html"
            net.show(ficheiro_saida, notebook=False)
            
            # Get absolute path
            caminho_absoluto = os.path.abspath(ficheiro_saida)
            arquivos_gerados.append(caminho_absoluto)
            
        except Exception as e:
            raise Exception(f"Error generating graph for query {idx + 1}: {str(e)}")
    
    return arquivos_gerados


class QueryParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Consultas SQL")
        self.root.geometry("900x750")
        
        # Store parsed queries
        self.lista_de_queries = None
        
        # Title
        title_label = tk.Label(root, text="Analisador de Consultas SQL", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Query input section
        input_label = tk.Label(root, text="Insira a Consulta SQL:", font=("Arial", 10, "bold"))
        input_label.pack(anchor="w", padx=10)
        
        self.query_text = scrolledtext.ScrolledText(
            root, 
            height=8, 
            width=100,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        self.query_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=False)
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        self.parse_button = tk.Button(
            button_frame, 
            text="Analisar Consulta", 
            command=self.parse_query,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.parse_button.pack(side=tk.LEFT, padx=5)
        
        self.generate_graph_button = tk.Button(
            button_frame,
            text="Gerar Gráficos",
            command=self.generate_graphs,
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.generate_graph_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="Limpar",
            command=self.clear_all,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_label = tk.Label(root, text="Saída / Erros:", font=("Arial", 10, "bold"))
        output_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.output_text = scrolledtext.ScrolledText(
            root,
            height=15,
            width=100,
            font=("Courier", 9),
            wrap=tk.WORD,
            bg="#f5f5f5"
        )
        self.output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Configure error highlighting
        self.output_text.tag_config("error", foreground="#d32f2f", font=("Courier", 9, "bold"))
        self.output_text.tag_config("success", foreground="#388e3c", font=("Courier", 9, "bold"))
        self.output_text.tag_config("info", foreground="#1976d2", font=("Courier", 9))
        
    def parse_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        
        if not query:
            self.display_error("Erro: Por favor, insira uma consulta SQL")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        try:
            self.display_message("Tokenizando consulta...\n", "info")
            tokens = tokenize(query)
            self.display_message(f"✓ Tokenização bem-sucedida! {len(tokens)} tokens encontrados\n\n", "success")
            
            self.display_message("Analisando consulta...\n", "info")
            lista_de_queries = parse(tokens)
            self.display_message(f"✓ Análise bem-sucedida! {len(lista_de_queries)} consulta(s) encontrada(s)\n\n", "success")
            
            self.display_message("Validando esquema...\n", "info")
            validar_schema(lista_de_queries, bd)


            
            # Store queries for later use
            self.lista_de_queries = lista_de_queries
            self.generate_graph_button.config(state=tk.NORMAL)
            
            self.display_message("Consultas Analisadas:\n", "info")
            self.output_text.insert(tk.END, json.dumps(lista_de_queries, indent=2, ensure_ascii=False), "info")
            for idx, query_data in enumerate(lista_de_queries):
                plano = gerar_grafo_networkx(query_data, bd)[1]

                expressao_algebra = gerar_algebra_relacional(query_data)
                self.display_message(f"\n\nÁlgebra Relacional:\n{expressao_algebra}\n")
                
                for i, passo in enumerate(plano, 1):
                    self.display_message("\n")
                    self.display_message(f"\n{i}. {passo}")
            
        except Exception as e:
            self.lista_de_queries = None
            self.generate_graph_button.config(state=tk.DISABLED)
            self.display_error(str(e))
            self.output_text.insert(tk.END, f"\n\nTraceback:\n{traceback.format_exc()}", "error")
    
    def generate_graphs(self):
        """Generate HTML graphs for the parsed queries"""
        if not self.lista_de_queries:
            self.display_error("Erro: Nenhuma consulta analisada disponível. Por favor, analise uma consulta primeiro.")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        try:
            self.display_message("Gerando gráficos...\n", "info")
            arquivos_gerados = gerar_grafos_html(self.lista_de_queries, bd)
            self.display_message(f"✓ Gráficos gerados com sucesso!\n\n", "success")
            
            self.display_message("Arquivos gerados:\n", "info")
            for arquivo in arquivos_gerados:
                self.output_text.insert(tk.END, f"  • {arquivo}\n", "info")
            
        except Exception as e:
            self.display_error(str(e))
            self.output_text.insert(tk.END, f"\n\nTraceback:\n{traceback.format_exc()}", "error")
    
    def display_error(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"❌ {message}", "error")
    
    def display_message(self, message, tag="info"):
        self.output_text.insert(tk.END, message, tag)
        self.output_text.see(tk.END)
    
    def clear_all(self):
        self.query_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.lista_de_queries = None
        self.generate_graph_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = QueryParserGUI(root)
    root.mainloop()
