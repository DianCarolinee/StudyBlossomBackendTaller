from app.services.gemini_service import gemini_service
import re


class ConceptMapService:
    """
    Servicio para generar mapas conceptuales en formato Mermaid
    """

    async def generate_concept_map(self, topic: str) -> str:
        """
        Genera un mapa conceptual en sintaxis Mermaid
        """
        try:
            system_instruction = """Eres un experto en crear mapas conceptuales usando la sintaxis de Mermaid."""

            prompt = f"""Genera un mapa conceptual usando la sintaxis de Mermaid para el tema: {topic}.

REGLA MÁS IMPORTANTE: El texto dentro de los nodos (entre '[corchetes]') NO DEBE contener NUNCA los siguientes caracteres: () / #

Reglas:
- Genera un diagrama de Mermaid 'graph TD'.
- El mapa debe conectar entre 5 y 10 conceptos clave.
- Conecta los conceptos de forma lógica usando 'A --> B'. NO añadas texto a las conexiones.
- Si necesitas separar palabras dentro de un nodo, usa espacios o guiones. Por ejemplo, en lugar de 'A[Nodo/Concepto(1)]', escribe 'A[Nodo - Concepto 1]'.
- El resultado debe ser una única cadena de texto válida para Mermaid.

Devuelve el resultado en formato JSON:
{{
  "mermaid_graph": "graph TD; A[Tema Principal]; B[Concepto Clave 1]; C[Concepto Clave 2]; D[Detalle A]; A --> B; A --> C; B --> D;"
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            mermaid_graph = response.get("mermaid_graph", "")

            if not mermaid_graph:
                raise Exception("No se generó el mapa conceptual")

            # Sanitizar el grafo
            mermaid_graph = self._sanitize_mermaid_graph(mermaid_graph)

            return mermaid_graph

        except Exception as e:
            raise Exception(f"Error generando mapa conceptual: {str(e)}")

    def _sanitize_mermaid_graph(self, graph: str) -> str:
        """
        Limpia el grafo de Mermaid para evitar errores de sintaxis
        """

        # Eliminar caracteres problemáticos dentro de corchetes
        def replace_match(match):
            content = match.group(1)
            sanitized_content = re.sub(r'[()/#]', '', content)
            return f'[{sanitized_content}]'

        sanitized = re.sub(r'\[([^\]]+)\]', replace_match, graph)
        return sanitized


# Instancia singleton
concept_map_service = ConceptMapService()