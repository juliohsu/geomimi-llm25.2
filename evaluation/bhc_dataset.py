from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class QuestionCategory(Enum):
    BASIC_CONCEPTS = "conceitos_basicos"
    METHODOLOGY = "metodologia"
    CALCULATIONS = "calculos"
    INDICES = "indices"
    APPLICATIONS = "aplicacoes"

class DifficultyLevel(Enum):
    BASIC = "basico"
    INTERMEDIATE = "intermediario"
    ADVANCED = "avancado"

@dataclass
class BHCQuestion:
    id: int
    question: str
    ground_truth: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    keywords: List[str]
    expected_concepts: List[str]
    evaluation_notes: str

class BHCDataset:
    
    def __init__(self):
        self.questions = self._create_dataset()
    
    def _create_dataset(self) -> List[BHCQuestion]:
        
        questions = [
            BHCQuestion(
                id=1,
                question="O que é o Balanço Hídrico Climatológico (BHC) e qual é sua finalidade?",
                ground_truth="O BHC é uma metodologia usada para quantificar a entrada e saída de água no sistema solo-planta-atmosfera. Sua finalidade é estimar a disponibilidade de água ao longo do tempo, permitindo analisar déficits e excedentes hídricos e fases de disponibilidade de água para a vegetação.",
                category=QuestionCategory.BASIC_CONCEPTS,
                difficulty=DifficultyLevel.BASIC,
                keywords=["balanço hídrico", "climatológico", "BHC", "finalidade", "metodologia"],
                expected_concepts=[
                    "sistema solo-planta-atmosfera",
                    "entrada e saída de água",
                    "disponibilidade hídrica",
                    "déficits e excedentes",
                    "vegetação"
                ],
                evaluation_notes="Resposta deve explicar conceito fundamental e aplicações práticas"
            ),
            
            BHCQuestion(
                id=2,
                question="Qual é a equação simplificada do BHC sem considerar irrigação e ascensão capilar?",
                ground_truth="ΔARM = P − ET − DP. Onde ΔARM é a variação do armazenamento de água no solo, P é a precipitação, ET é a evapotranspiração e DP é a drenagem profunda.",
                category=QuestionCategory.CALCULATIONS,
                difficulty=DifficultyLevel.INTERMEDIATE,
                keywords=["equação", "simplificada", "irrigação", "ascensão capilar", "ΔARM"],
                expected_concepts=[
                    "variação do armazenamento",
                    "precipitação",
                    "evapotranspiração",
                    "drenagem profunda",
                    "componentes do balanço"
                ],
                evaluation_notes="Deve incluir fórmula exata e definir cada variável"
            ),
            
            BHCQuestion(
                id=3,
                question="O que representa a Evapotranspiração Potencial (ETP) e qual método é usado para calculá-la?",
                ground_truth="A ETP representa a quantidade máxima de água que poderia ser transferida para a atmosfera por evaporação e transpiração, assumindo água ilimitada. É calculada pelo método de Thornthwaite (1955), considerando temperatura média mensal e fotoperíodo.",
                category=QuestionCategory.METHODOLOGY,
                difficulty=DifficultyLevel.INTERMEDIATE,
                keywords=["evapotranspiração potencial", "ETP", "Thornthwaite", "método", "cálculo"],
                expected_concepts=[
                    "quantidade máxima de água",
                    "evaporação e transpiração",
                    "água ilimitada",
                    "método de Thornthwaite",
                    "temperatura média mensal",
                    "fotoperíodo"
                ],
                evaluation_notes="Deve explicar conceito de ETP e mencionar método específico"
            ),
            
            BHCQuestion(
                id=4,
                question="Como é determinado o Armazenamento de Água no Solo (ARM) no BHC?",
                ground_truth="O ARM indica a quantidade de água disponível no solo, limitado pela Capacidade de Água Disponível (CAD). Ele é atualizado mensalmente conforme a diferença entre precipitação e demanda hídrica (P−ETP), variando entre 0 e CAD.",
                category=QuestionCategory.METHODOLOGY,
                difficulty=DifficultyLevel.INTERMEDIATE,
                keywords=["armazenamento", "ARM", "solo", "CAD", "capacidade"],
                expected_concepts=[
                    "água disponível no solo",
                    "Capacidade de Água Disponível",
                    "atualização mensal",
                    "diferença P-ETP",
                    "limites 0 e CAD"
                ],
                evaluation_notes="Deve explicar como ARM é calculado e seus limites"
            ),
            
            BHCQuestion(
                id=5,
                question="Qual é a diferença entre Evapotranspiração Real (ETR) e Déficit Hídrico (DEF)?",
                ground_truth="A ETR é a quantidade de água que a vegetação realmente consome, considerando a disponibilidade no solo. O DEF ocorre quando a demanda de evapotranspiração não é atendida integralmente, mostrando o estresse hídrico da vegetação: DEF = ETP − ETR.",
                category=QuestionCategory.BASIC_CONCEPTS,
                difficulty=DifficultyLevel.INTERMEDIATE,
                keywords=["ETR", "DEF", "evapotranspiração real", "déficit hídrico", "diferença"],
                expected_concepts=[
                    "consumo real de água",
                    "disponibilidade no solo",
                    "demanda não atendida",
                    "estresse hídrico",
                    "fórmula DEF = ETP - ETR"
                ],
                evaluation_notes="Deve contrastar ETR e DEF, incluindo a relação matemática"
            ),
            
            BHCQuestion(
                id=6,
                question="O que significa Excedente Hídrico (EXC) e quando ele ocorre?",
                ground_truth="EXC representa a água que sobra quando o solo já atingiu a capacidade máxima (CAD) e ainda há precipitação. Ele indica água disponível para escoamento superficial ou recarga de aquíferos.",
                category=QuestionCategory.BASIC_CONCEPTS,
                difficulty=DifficultyLevel.BASIC,
                keywords=["excedente hídrico", "EXC", "capacidade máxima", "precipitação"],
                expected_concepts=[
                    "água que sobra",
                    "capacidade máxima do solo",
                    "precipitação excedente",
                    "escoamento superficial",
                    "recarga de aquíferos"
                ],
                evaluation_notes="Deve explicar condições para ocorrência de excedente"
            ),
            
            BHCQuestion(
                id=7,
                question="Quais são os índices climáticos calculados a partir do BHC e qual a função de cada um?",
                ground_truth="Índice de Aridez (Ia): quantifica a deficiência de água em relação à demanda atmosférica. Índice Hídrico (Ih): quantifica o excedente de água em relação à demanda atmosférica. Índice de Umidade (Iu): combina Ia e Ih para classificar o tipo de clima, indicando se é úmido ou seco.",
                category=QuestionCategory.INDICES,
                difficulty=DifficultyLevel.ADVANCED,
                keywords=["índices climáticos", "aridez", "hídrico", "umidade", "Ia", "Ih", "Iu"],
                expected_concepts=[
                    "Índice de Aridez (Ia)",
                    "Índice Hídrico (Ih)",
                    "Índice de Umidade (Iu)",
                    "deficiência de água",
                    "excedente de água",
                    "demanda atmosférica",
                    "classificação climática"
                ],
                evaluation_notes="Deve listar todos os três índices e suas funções específicas"
            ),
            
            BHCQuestion(
                id=8,
                question="Como o tipo de clima é classificado com base no Índice de Umidade (Iu)?",
                ground_truth="O tipo de clima é determinado por faixas de Iu: Iu ≥ 100 → Superúmido (A), 80 ≤ Iu < 100 → Úmido (B4). Outros valores seguem categorias intermediárias até Árido (E).",
                category=QuestionCategory.INDICES,
                difficulty=DifficultyLevel.ADVANCED,
                keywords=["classificação climática", "índice de umidade", "Iu", "faixas", "categorias"],
                expected_concepts=[
                    "faixas de valores de Iu",
                    "Superúmido (A)",
                    "Úmido (B4)",
                    "categorias intermediárias",
                    "Árido (E)",
                    "classificação de clima"
                ],
                evaluation_notes="Deve incluir valores numéricos das faixas e códigos de classificação"
            ),
            
            BHCQuestion(
                id=9,
                question="Qual é o objetivo da etapa de coleta e preparação de dados no aplicativo Climate Index?",
                ground_truth="Transformar dados climáticos diários brutos em dados mensais confiáveis, limpos e consistentes, para que o cálculo do balanço hídrico seja preciso.",
                category=QuestionCategory.APPLICATIONS,
                difficulty=DifficultyLevel.BASIC,
                keywords=["coleta", "preparação", "dados", "Climate Index", "objetivo"],
                expected_concepts=[
                    "dados climáticos diários",
                    "dados mensais",
                    "confiabilidade",
                    "limpeza de dados",
                    "consistência",
                    "precisão do cálculo"
                ],
                evaluation_notes="Deve enfatizar transformação de dados e qualidade"
            ),
            
            BHCQuestion(
                id=10,
                question="Quais dados são obrigatórios para a execução do BHC no aplicativo e quais são opcionais?",
                ground_truth="Obrigatórios: Precipitação (P) e temperatura média (Tm). Opcionais: Umidade relativa (UR), velocidade do vento (VV) e radiação solar (RadSol). Eles podem ser usados para metodologias mais complexas, como Penman-Monteith.",
                category=QuestionCategory.APPLICATIONS,
                difficulty=DifficultyLevel.INTERMEDIATE,
                keywords=["dados obrigatórios", "opcionais", "precipitação", "temperatura", "aplicativo"],
                expected_concepts=[
                    "Precipitação (P)",
                    "temperatura média (Tm)",
                    "Umidade relativa (UR)",
                    "velocidade do vento (VV)",
                    "radiação solar (RadSol)",
                    "metodologias complexas",
                    "Penman-Monteith"
                ],
                evaluation_notes="Deve separar claramente dados obrigatórios de opcionais"
            )
        ]
        
        return questions
    
    def get_all_questions(self) -> List[BHCQuestion]:
        return self.questions
    
    def get_questions_by_category(self, category: QuestionCategory) -> List[BHCQuestion]:
        return [q for q in self.questions if q.category == category]
    
    def get_questions_by_difficulty(self, difficulty: DifficultyLevel) -> List[BHCQuestion]:
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def get_question_by_id(self, question_id: int) -> BHCQuestion:
        for question in self.questions:
            if question.id == question_id:
                return question
        raise ValueError(f"Question with ID {question_id} not found")
    
    def to_dict_format(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": q.id,
                "question": q.question,
                "ground_truth": q.ground_truth,
                "category": q.category.value,
                "difficulty": q.difficulty.value,
                "keywords": q.keywords,
                "expected_concepts": q.expected_concepts,
                "evaluation_notes": q.evaluation_notes
            }
            for q in self.questions
        ]
    
    def get_evaluation_subset(self, max_questions: int = 5) -> List[BHCQuestion]:
        basic_questions = self.get_questions_by_difficulty(DifficultyLevel.BASIC)[:2]
        intermediate_questions = self.get_questions_by_difficulty(DifficultyLevel.INTERMEDIATE)[:2]
        advanced_questions = self.get_questions_by_difficulty(DifficultyLevel.ADVANCED)[:1]
        
        subset = basic_questions + intermediate_questions + advanced_questions
        return subset[:max_questions]
    
    def get_statistics(self) -> Dict[str, Any]:
        category_counts = {}
        for category in QuestionCategory:
            category_counts[category.value] = len(self.get_questions_by_category(category))
        
        difficulty_counts = {}
        for difficulty in DifficultyLevel:
            difficulty_counts[difficulty.value] = len(self.get_questions_by_difficulty(difficulty))
        
        return {
            "total_questions": len(self.questions),
            "categories": category_counts,
            "difficulty_levels": difficulty_counts,
            "average_question_length": sum(len(q.question) for q in self.questions) / len(self.questions),
            "average_answer_length": sum(len(q.ground_truth) for q in self.questions) / len(self.questions),
            "total_keywords": sum(len(q.keywords) for q in self.questions),
            "total_concepts": sum(len(q.expected_concepts) for q in self.questions)
        }
    
    def search_questions(self, query: str) -> List[BHCQuestion]:
        query_lower = query.lower()
        matching_questions = []
        
        for question in self.questions:
            if query_lower in question.question.lower():
                matching_questions.append(question)
                continue
            
            if any(query_lower in keyword.lower() for keyword in question.keywords):
                matching_questions.append(question)
                continue
            
            if any(query_lower in concept.lower() for concept in question.expected_concepts):
                matching_questions.append(question)
                continue
        
        return matching_questions

bhc_dataset = BHCDataset()

def get_all_questions() -> List[BHCQuestion]:
    return bhc_dataset.get_all_questions()

def get_evaluation_subset(max_questions: int = 5) -> List[BHCQuestion]:
    return bhc_dataset.get_evaluation_subset(max_questions)

def get_questions_dict() -> List[Dict[str, Any]]:
    return bhc_dataset.to_dict_format()

def search_bhc_questions(query: str) -> List[BHCQuestion]:
    return bhc_dataset.search_questions(query)

def get_dataset_stats() -> Dict[str, Any]:
    return bhc_dataset.get_statistics()