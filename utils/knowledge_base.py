# utils/knowledge_base.py

"""
Comprehensive Clinical Knowledge Base for laboratory interpretation.
Covers Complete Blood Count (CBC), Metabolic, Liver, Renal, Lipid, and Thyroid panels.
"""

MEDICAL_KNOWLEDGE = {
    # ── Complete Blood Count (CBC) ──────────────────────────
    "wbc_count": {
        "definition": "White blood cells defend the body against infections, inflammation, and foreign pathogens.",
        "functions": ["Immune defense", "Pathogen neutralization", "Inflammatory response"],
        "common_causes_low": ["Viral infections", "Bone marrow suppression", "Autoimmune conditions"],
        "common_causes_high": ["Bacterial infection", "Acute inflammation", "Physical stress", "Leukemia"]
    },
    "rbc_count": {
        "definition": "Red blood cells contain hemoglobin and are responsible for delivering oxygen to tissues throughout the body.",
        "functions": ["Oxygen delivery", "Carbon dioxide removal"],
        "common_causes_low": ["Anemia", "Blood loss", "Nutritional deficiencies (iron, B12, folate)"],
        "common_causes_high": ["Dehydration", "Chronic hypoxia (smoking, COPD)", "Polycythemia vera"]
    },
    "hemoglobin": {
        "definition": "An iron-rich protein inside red blood cells that binds oxygen in the lungs and releases it into body tissues.",
        "functions": ["Oxygen transport", "Systemic tissue oxygenation"],
        "common_causes_low": ["Iron deficiency anemia", "Chronic disease anemia", "Active blood loss"],
        "common_causes_high": ["Dehydration", "High altitude acclimation", "Smoking", "Polycythemia"]
    },
    "hematocrit": {
        "definition": "The proportion of total blood volume occupied by red blood cells, expressed as a percentage.",
        "functions": ["Assessment of red blood cell mass and blood viscosity"],
        "common_causes_low": ["Anemia", "Overhydration", "Blood loss"],
        "common_causes_high": ["Dehydration", "Polycythemia", "Chronic hypoxia"]
    },
    "mcv": {
        "definition": "Mean Corpuscular Volume measures the average physical size of individual red blood cells.",
        "functions": ["Classification of anemia (microcytic vs normocytic vs macrocytic)"],
        "common_causes_low": ["Iron deficiency anemia", "Thalassemia trait"],
        "common_causes_high": ["Vitamin B12 deficiency", "Folate deficiency", "Liver disease"]
    },
    "mch": {
        "definition": "Mean Corpuscular Hemoglobin quantifies the average amount of hemoglobin contained within each red blood cell.",
        "functions": ["Indicator of cellular hemoglobin content"],
        "common_causes_low": ["Microcytic / hypochromic anemia (iron deficiency)"],
        "common_causes_high": ["Macrocytic anemia (B12 / folate deficiency)"]
    },
    "mchc": {
        "definition": "Mean Corpuscular Hemoglobin Concentration measures the average concentration of hemoglobin in a given volume of packed red blood cells.",
        "functions": ["Assessment of cellular chromasia (color/density)"],
        "common_causes_low": ["Iron deficiency anemia", "Chronic blood loss"],
        "common_causes_high": ["Spherocytosis", "Severe dehydration", "Cold agglutinins"]
    },
    "rdw": {
        "definition": "Red Cell Distribution Width measures the degree of variation in red blood cell volume and size (anisocytosis).",
        "functions": ["Differentiating mixed anemias and early nutritional deficiency"],
        "common_causes_low": ["Generally normal, indicates uniform cell size"],
        "common_causes_high": ["Iron deficiency anemia", "Mixed nutritional deficiencies", "Hemoglobinopathies"]
    },
    "rdw_sd": {
        "definition": "RDW Standard Deviation measures the actual spread of the red blood cell histogram width in femtoliters.",
        "functions": ["Evaluates red cell size variation directly"],
        "common_causes_low": ["Normal variation"],
        "common_causes_high": ["Anisocytosis", "Iron deficiency"]
    },
    "platelets": {
        "definition": "Small disc-shaped cell fragments essential for normal blood clotting and vascular repair.",
        "functions": ["Primary hemostasis", "Clot formation", "Vascular integrity"],
        "common_causes_low": ["Immune thrombocytopenia", "Viral illness", "Bone marrow suppression", "Medications"],
        "common_causes_high": ["Reactive thrombocytosis (infection, inflammation)", "Iron deficiency", "Myeloproliferative disorders"]
    },
    "mpv": {
        "definition": "Mean Platelet Volume reflects the average size of circulating platelets, correlating with platelet production rate in bone marrow.",
        "functions": ["Marker of platelet turnover and thrombopoiesis"],
        "common_causes_low": ["Aplastic anemia", "Impaired bone marrow production"],
        "common_causes_high": ["Immune destruction with compensatory bone marrow release", "Cardiovascular risk factor"]
    },
    "neutrophils_pct": {
        "definition": "Neutrophils are the primary white blood cells responsible for acute defense against bacterial infections.",
        "functions": ["Phagocytosis of bacteria", "First responder to acute tissue injury"],
        "common_causes_low": ["Viral infections", "Medication effects", "Severe sepsis"],
        "common_causes_high": ["Acute bacterial infection", "Inflammation", "Glucocorticoid use", "Physical stress"]
    },
    "neutrophils_abs": {
        "definition": "Absolute Neutrophil Count (ANC) reflects the absolute number of circulating neutrophils per unit volume of blood.",
        "functions": ["Primary measure of immune competence against bacterial infection"],
        "common_causes_low": ["Neutropenia", "Chemotherapy", "Severe viral illness"],
        "common_causes_high": ["Bacterial infection", "Acute inflammation", "Systemic stress"]
    },
    "lymphocytes_pct": {
        "definition": "Lymphocytes (T cells, B cells, NK cells) coordinate adaptive immunity, antibody production, and viral defense.",
        "functions": ["Cell-mediated immunity", "Humoral antibody response", "Viral surveillance"],
        "common_causes_low": ["Corticosteroid therapy", "Immunodeficiency", "Acute severe illness"],
        "common_causes_high": ["Viral infections (EBV, CMV)", "Chronic lymphocytic leukemia", "Pertussis"]
    },
    "lymphocytes_abs": {
        "definition": "Absolute Lymphocyte Count (ALC) represents the total number of circulating lymphocytes in peripheral blood.",
        "functions": ["Marker of adaptive immune reserve"],
        "common_causes_low": ["Lymphopenia", "Immunosuppression"],
        "common_causes_high": ["Acute viral infection", "Lymphocytosis"]
    },
    "monocytes_pct": {
        "definition": "Monocytes are mononuclear leukocytes that migrate into tissues to become macrophages and dendritic cells.",
        "functions": ["Phagocytosis", "Antigen presentation", "Chronic inflammation resolution"],
        "common_causes_low": ["Aplastic states", "Hairy cell leukemia"],
        "common_causes_high": ["Chronic infections (tuberculosis, endocarditis)", "Inflammatory bowel disease"]
    },
    "monocytes_abs": {
        "definition": "Absolute Monocyte Count (AMC) measures total circulating monocytes in the bloodstream.",
        "functions": ["Marker of macrophage reserve"],
        "common_causes_low": ["Bone marrow depression"],
        "common_causes_high": ["Chronic infection or recovery phase of acute infection"]
    },
    "eosinophils_pct": {
        "definition": "Eosinophils participate in allergic responses, asthma pathogenesis, and host defense against parasitic organisms.",
        "functions": ["Allergic mediation", "Anti-parasitic activity"],
        "common_causes_low": ["Acute stress response", "Corticosteroid administration"],
        "common_causes_high": ["Allergies", "Asthma", "Parasitic infection", "Drug reactions"]
    },
    "eosinophils_abs": {
        "definition": "Absolute Eosinophil Count (AEC) measures the exact concentration of circulating eosinophils.",
        "functions": ["Assessment of allergic and parasitic inflammatory activity"],
        "common_causes_low": ["Stress leukogram"],
        "common_causes_high": ["Eosinophilia", "Atopic disease", "Helminthic infections"]
    },
    "basophils_pct": {
        "definition": "Basophils release histamine and heparin during hypersensitivity reactions and promote acute allergic responses.",
        "functions": ["Histamine release", "Immediate hypersensitivity mediation"],
        "common_causes_low": ["Normal finding; clinical significance is rare"],
        "common_causes_high": ["Myeloproliferative neoplasms (CML)", "Allergic disorders"]
    },
    "basophils_abs": {
        "definition": "Absolute Basophil Count (ABC) quantifies circulating basophils in peripheral blood.",
        "functions": ["Evaluation of basophilia and hypersensitivity reactions"],
        "common_causes_low": ["Usually within expected range"],
        "common_causes_high": ["Basophilia, chronic myeloid leukemia"]
    },

    # ── Metabolic & Chemistry ──────────────────────────────
    "fasting_glucose": {
        "definition": "Blood glucose measures circulating simple sugar after an overnight fast of at least 8 hours.",
        "functions": ["Primary energy currency for cells and neural tissues"],
        "common_causes_low": ["Hypoglycemia", "Excess insulin", "Prolonged fasting"],
        "common_causes_high": ["Diabetes mellitus", "Prediabetes", "Acute physiologic stress"]
    },
    "hba1c": {
        "definition": "Hemoglobin A1c reflects the average percentage of glycated hemoglobin over the prior 2 to 3 months.",
        "functions": ["Long-term glycemic monitoring and diabetes diagnosis"],
        "common_causes_low": ["Hemolytic anemia", "Recent blood transfusion"],
        "common_causes_high": ["Poor glycemic control", "Unmanaged diabetes"]
    },
    "creatinine": {
        "definition": "Creatinine is a metabolic byproduct of muscle creatine breakdown, filtered freely by renal glomeruli.",
        "functions": ["Key surrogate biomarker of glomerular filtration rate (GFR)"],
        "common_causes_low": ["Low muscle mass", "Malnutrition"],
        "common_causes_high": ["Acute kidney injury", "Chronic kidney disease", "Dehydration"]
    },
    "urea": {
        "definition": "Blood urea nitrogen is a nitrogenous waste product formed by hepatic protein catabolism, excreted by kidneys.",
        "functions": ["Marker of renal clearance and protein metabolism"],
        "common_causes_low": ["Low protein intake", "Severe liver failure"],
        "common_causes_high": ["Prerenal azotemia (dehydration)", "Renal impairment", "High protein intake"]
    },
    "bun": {
        "definition": "Blood Urea Nitrogen measures the amount of nitrogen in blood that comes from urea waste product.",
        "functions": ["Renal filtration and fluid balance evaluation"],
        "common_causes_low": ["Malnutrition", "Severe hepatic disease"],
        "common_causes_high": ["Dehydration", "Renal dysfunction", "GI bleeding"]
    },

    # ── Liver Function ──────────────────────────────────────
    "alt": {
        "definition": "Alanine Aminotransferase (ALT/SGPT) is a cytoplasmic enzyme found predominantly in hepatocytes.",
        "functions": ["Sensitive biomarker for hepatocellular injury"],
        "common_causes_low": ["Generally normal"],
        "common_causes_high": ["Viral hepatitis", "Metabolic dysfunction-associated steatohepatitis (MASH)", "Drug toxicity"]
    },
    "ast": {
        "definition": "Aspartate Aminotransferase (AST/SGOT) is an enzyme found in liver, heart, skeletal muscle, and kidneys.",
        "functions": ["Marker of hepatocellular damage and muscular injury"],
        "common_causes_low": ["Generally normal"],
        "common_causes_high": ["Alcoholic liver injury", "Hepatitis", "Strenuous exercise", "Myocardial infarction"]
    },
    "alp": {
        "definition": "Alkaline Phosphatase (ALP) is an enzyme found concentrated in bile ducts and bone tissue.",
        "functions": ["Marker of biliary flow obstruction and bone turnover"],
        "common_causes_low": ["Malnutrition", "Zinc deficiency"],
        "common_causes_high": ["Cholestasis", "Biliary obstruction", "Active bone growth/healing"]
    },
    "bilirubin_total": {
        "definition": "Total Bilirubin measures the yellowish pigment formed from the physiological breakdown of heme.",
        "functions": ["Evaluation of liver clearance, biliary drainage, and hemolysis"],
        "common_causes_low": ["Generally normal"],
        "common_causes_high": ["Hemolysis", "Gilbert syndrome", "Hepatic parenchymal disease", "Biliary obstruction"]
    },

    # ── Lipids ──────────────────────────────────────────────
    "total_cholesterol": {
        "definition": "Total cholesterol represents the total circulating sum of LDL, HDL, and VLDL cholesterol in serum.",
        "functions": ["Cell membrane structure", "Steroid hormone synthesis"],
        "common_causes_low": ["Severe hyperthyroidism", "Severe malabsorption"],
        "common_causes_high": ["Familial hypercholesterolemia", "Dietary intake", "Atherosclerotic cardiovascular risk"]
    },
    "triglycerides": {
        "definition": "Triglycerides are the main storage form of dietary lipids and fat energy transported in the blood.",
        "functions": ["Energy storage and lipid metabolic reserve"],
        "common_causes_low": ["Malnutrition", "Extreme low-fat diet"],
        "common_causes_high": ["Metabolic syndrome", "High carbohydrate diet", "Alcohol excess", "Pancreatitis risk"]
    },
    "hdl": {
        "definition": "High-Density Lipoprotein ('good' cholesterol) transports excess cholesterol from tissues back to the liver.",
        "functions": ["Reverse cholesterol transport", "Anti-atherogenic protection"],
        "common_causes_low": ["Metabolic syndrome", "Physical inactivity", "Smoking"],
        "common_causes_high": ["Regular cardiovascular exercise", "Genetic factors"]
    },
    "ldl": {
        "definition": "Low-Density Lipoprotein ('bad' cholesterol) carries cholesterol particles to peripheral tissues and artery walls.",
        "functions": ["Peripheral cholesterol delivery; key driver of arterial plaque formation"],
        "common_causes_low": ["Malnutrition", "Genetic hypobetalipoproteinemia"],
        "common_causes_high": ["Atherosclerotic cardiovascular disease risk", "Saturated fat intake"]
    },

    # ── Thyroid ─────────────────────────────────────────────
    "tsh": {
        "definition": "Thyroid Stimulating Hormone is released by the pituitary gland to regulate thyroid hormone production.",
        "functions": ["Master regulator of thyroid hormone secretion and basal metabolism"],
        "common_causes_low": ["Hyperthyroidism", "Excess thyroid medication"],
        "common_causes_high": ["Primary hypothyroidism", "Hashimoto thyroiditis"]
    }
}
