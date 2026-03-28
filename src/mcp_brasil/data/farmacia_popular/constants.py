"""Constants for the Farmácia Popular feature."""

# Reuses CNES API for establishment search (pharmacies are in CNES)
CNES_API_BASE = "https://apidadosabertos.saude.gov.br/cnes"
ESTABELECIMENTOS_URL = f"{CNES_API_BASE}/estabelecimentos"

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# CNES type codes for pharmacies
TIPO_FARMACIA = "43"  # Farmácia

# Medications from Farmácia Popular organized by therapeutic indication.
# All medications became 100% free in February 2023.
# Source: Ministério da Saúde — Programa Farmácia Popular do Brasil.
MEDICAMENTOS: list[dict[str, str | bool]] = [
    # --- Hipertensão ---
    {
        "nome": "Atenolol",
        "principio_ativo": "Atenolol",
        "apresentacao": "Comprimido 25mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Captopril",
        "principio_ativo": "Captopril",
        "apresentacao": "Comprimido 25mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Propranolol",
        "principio_ativo": "Cloridrato de Propranolol",
        "apresentacao": "Comprimido 40mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Hidroclorotiazida",
        "principio_ativo": "Hidroclorotiazida",
        "apresentacao": "Comprimido 25mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Losartana",
        "principio_ativo": "Losartana Potássica",
        "apresentacao": "Comprimido 50mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Enalapril",
        "principio_ativo": "Maleato de Enalapril",
        "apresentacao": "Comprimido 10mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    {
        "nome": "Anlodipino",
        "principio_ativo": "Besilato de Anlodipino",
        "apresentacao": "Comprimido 5mg",
        "indicacao": "Hipertensão",
        "gratuito": True,
    },
    # --- Diabetes ---
    {
        "nome": "Metformina 500mg",
        "principio_ativo": "Cloridrato de Metformina",
        "apresentacao": "Comprimido 500mg",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    {
        "nome": "Metformina 500mg AP",
        "principio_ativo": "Cloridrato de Metformina",
        "apresentacao": "Comprimido 500mg Ação Prolongada",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    {
        "nome": "Metformina 850mg",
        "principio_ativo": "Cloridrato de Metformina",
        "apresentacao": "Comprimido 850mg",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    {
        "nome": "Glibenclamida",
        "principio_ativo": "Glibenclamida",
        "apresentacao": "Comprimido 5mg",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    {
        "nome": "Insulina NPH",
        "principio_ativo": "Insulina Humana NPH",
        "apresentacao": "Suspensão Injetável 100UI/ml",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    {
        "nome": "Insulina Regular",
        "principio_ativo": "Insulina Humana Regular",
        "apresentacao": "Solução Injetável 100UI/ml",
        "indicacao": "Diabetes",
        "gratuito": True,
    },
    # --- Asma ---
    {
        "nome": "Beclometasona 200mcg",
        "principio_ativo": "Dipropionato de Beclometasona",
        "apresentacao": "Aerosol 200mcg/dose",
        "indicacao": "Asma",
        "gratuito": True,
    },
    {
        "nome": "Beclometasona 250mcg",
        "principio_ativo": "Dipropionato de Beclometasona",
        "apresentacao": "Aerosol 250mcg/dose",
        "indicacao": "Asma",
        "gratuito": True,
    },
    {
        "nome": "Beclometasona 50mcg",
        "principio_ativo": "Dipropionato de Beclometasona",
        "apresentacao": "Spray Nasal Aquoso 50mcg/dose",
        "indicacao": "Asma",
        "gratuito": True,
    },
    {
        "nome": "Salbutamol",
        "principio_ativo": "Sulfato de Salbutamol",
        "apresentacao": "Aerosol 100mcg/dose",
        "indicacao": "Asma",
        "gratuito": True,
    },
    {
        "nome": "Ipratrópio Solução",
        "principio_ativo": "Brometo de Ipratrópio",
        "apresentacao": "Solução para Inalação 0,25mg/ml",
        "indicacao": "Asma",
        "gratuito": True,
    },
    {
        "nome": "Ipratrópio Aerosol",
        "principio_ativo": "Brometo de Ipratrópio",
        "apresentacao": "Aerosol 0,02mg/dose",
        "indicacao": "Asma",
        "gratuito": True,
    },
    # --- Rinite ---
    {
        "nome": "Budesonida 32mcg",
        "principio_ativo": "Budesonida",
        "apresentacao": "Spray Nasal 32mcg/dose",
        "indicacao": "Rinite",
        "gratuito": True,
    },
    {
        "nome": "Budesonida 50mcg",
        "principio_ativo": "Budesonida",
        "apresentacao": "Spray Nasal 50mcg/dose",
        "indicacao": "Rinite",
        "gratuito": True,
    },
    # --- Doença de Parkinson ---
    {
        "nome": "Benserazida + Levodopa",
        "principio_ativo": "Cloridrato de Benserazida + Levodopa",
        "apresentacao": "Comprimido 25mg + 100mg",
        "indicacao": "Doença de Parkinson",
        "gratuito": True,
    },
    {
        "nome": "Carbidopa + Levodopa",
        "principio_ativo": "Carbidopa + Levodopa",
        "apresentacao": "Comprimido 25mg + 250mg",
        "indicacao": "Doença de Parkinson",
        "gratuito": True,
    },
    # --- Osteoporose ---
    {
        "nome": "Alendronato de Sódio",
        "principio_ativo": "Alendronato de Sódio",
        "apresentacao": "Comprimido 70mg",
        "indicacao": "Osteoporose",
        "gratuito": True,
    },
    # --- Glaucoma ---
    {
        "nome": "Timolol 2,5mg/ml",
        "principio_ativo": "Maleato de Timolol",
        "apresentacao": "Solução Oftálmica 2,5mg/ml",
        "indicacao": "Glaucoma",
        "gratuito": True,
    },
    {
        "nome": "Timolol 5mg/ml",
        "principio_ativo": "Maleato de Timolol",
        "apresentacao": "Solução Oftálmica 5mg/ml",
        "indicacao": "Glaucoma",
        "gratuito": True,
    },
    # --- Contraceptivos ---
    {
        "nome": "Medroxiprogesterona",
        "principio_ativo": "Acetato de Medroxiprogesterona",
        "apresentacao": "Suspensão Injetável 150mg/ml",
        "indicacao": "Contracepção",
        "gratuito": True,
    },
    {
        "nome": "Etinilestradiol + Noretisterona",
        "principio_ativo": "Etinilestradiol + Noretisterona",
        "apresentacao": "Comprimido 0,03mg + 0,15mg",
        "indicacao": "Contracepção",
        "gratuito": True,
    },
    {
        "nome": "Noretisterona",
        "principio_ativo": "Noretisterona",
        "apresentacao": "Comprimido 0,35mg",
        "indicacao": "Contracepção",
        "gratuito": True,
    },
    {
        "nome": "Valerato de Estradiol + Noretisterona",
        "principio_ativo": "Valerato de Estradiol + Enantato de Noretisterona",
        "apresentacao": "Solução Injetável 50mg + 5mg",
        "indicacao": "Contracepção",
        "gratuito": True,
    },
    # --- Dislipidemia ---
    {
        "nome": "Sinvastatina 10mg",
        "principio_ativo": "Sinvastatina",
        "apresentacao": "Comprimido 10mg",
        "indicacao": "Dislipidemia",
        "gratuito": True,
    },
    {
        "nome": "Sinvastatina 20mg",
        "principio_ativo": "Sinvastatina",
        "apresentacao": "Comprimido 20mg",
        "indicacao": "Dislipidemia",
        "gratuito": True,
    },
    {
        "nome": "Sinvastatina 40mg",
        "principio_ativo": "Sinvastatina",
        "apresentacao": "Comprimido 40mg",
        "indicacao": "Dislipidemia",
        "gratuito": True,
    },
]

# All therapeutic indications covered by the program
INDICACOES: list[str] = [
    "Hipertensão",
    "Diabetes",
    "Asma",
    "Rinite",
    "Doença de Parkinson",
    "Osteoporose",
    "Glaucoma",
    "Contracepção",
    "Dislipidemia",
]

# Required documents for withdrawal
DOCUMENTOS_RETIRADA: list[str] = [
    "Documento de identificação com foto (RG, CNH, etc.)",
    "CPF",
    "Receita médica dentro do prazo de validade (120 dias)",
    "Receita emitida por profissional do SUS ou particular",
]

# Eligibility rules summary
REGRAS_ELEGIBILIDADE: str = (
    "Qualquer pessoa com receita médica válida (SUS ou particular) pode retirar "
    "medicamentos gratuitos em farmácias credenciadas ao Programa Farmácia Popular. "
    "Desde fevereiro de 2023, todos os medicamentos do programa são 100%% gratuitos. "
    "É necessário apresentar documento com foto, CPF e receita médica com validade "
    "de até 120 dias. A quantidade dispensada segue a prescrição médica, limitada "
    "ao período de tratamento."
)
