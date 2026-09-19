"""
analyse_reglements_tools.py
analyserReglements : total cashed, split by payment mode and by client.
detecterAnomalies  : compares computed TTC per invoice with amounts paid.
"""
from fastmcp import FastMCP
from api.myApi import api_get, _extraire_erreur

mcp = FastMCP("Facturation")


def _list_from(endpoint: str, alt_key: str) -> list:
    data = api_get(endpoint)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("data") or data.get("items") or data.get(alt_key) or []
    return []


def _get_reglements():
    return _list_from("/reglements/", "reglements")

def _get_factures():
    return _list_from("/factures/", "factures")

def _get_lignes_facture():
    return _list_from("/lignes-facture/", "lignes")


# TOOL 1 : analyserReglements
@mcp.tool(name="analyserReglements",
          description="Analyse globale des règlements : total encaissé, répartition par mode de paiement et par client.")
def analyser_reglements(id_client: int | None = None) -> dict:
    try:
        reglements = _get_reglements()
        factures = {f["id_facture"]: f for f in _get_factures()}

        total_encaisse = 0.0
        par_mode = {}
        par_client = {}
        nombre = 0

        for r in reglements:
            facture = factures.get(r.get("id_facture"), {})
            client_id = facture.get("id_client")

            # optional filter by client
            if id_client is not None and client_id != id_client:
                continue

            montant = float(r.get("montant", 0))
            mode = r.get("mode") or "Inconnu"

            nombre += 1
            total_encaisse += montant
            par_mode[mode] = par_mode.get(mode, 0.0) + montant
            if client_id:
                par_client[client_id] = par_client.get(client_id, 0.0) + montant

        return {
            "ok": True,
            "total_encaisse": round(total_encaisse, 2),
            "nombre_reglements": nombre,
            "ventilation_par_mode": par_mode,
            "ventilation_par_client": par_client,
        }
    except Exception as err:
        return {"ok": False, "message": "API error", "error": _extraire_erreur(err)}


# TOOL 2 : detecterAnomalies
@mcp.tool(name="detecterAnomalies",
          description="Détecte les écarts entre le montant TTC calculé des factures et le total réellement réglé, ainsi que les statuts incohérents.")
def detecter_anomalies() -> dict:
    try:
        factures = _get_factures()
        lignes = _get_lignes_facture()
        reglements = _get_reglements()

        # 1. TTC per invoice
        ttc_par_facture = {}
        for l in lignes:
            id_f = l.get("id_facture")
            ht = float(l.get("prix_vente_ht", 0)) * float(l.get("quantite", 0))
            tva = float(l.get("taux_tva", 0)) / 100
            ttc_par_facture[id_f] = ttc_par_facture.get(id_f, 0.0) + ht * (1 + tva)

        # 2. Payments per invoice
        paye_par_facture = {}
        for r in reglements:
            id_f = r.get("id_facture")
            paye_par_facture[id_f] = paye_par_facture.get(id_f, 0.0) + float(r.get("montant", 0))

        # 3. Compare
        anomalies = []
        for f in factures:
            id_f = f.get("id_facture")
            statut = f.get("statut")
            ttc_attendu = round(ttc_par_facture.get(id_f, 0.0), 2)
            total_paye = round(paye_par_facture.get(id_f, 0.0), 2)
            ecart = round(total_paye - ttc_attendu, 2)

            if abs(ecart) > 0.01:
                anomalies.append({
                    "id_facture": id_f,
                    "type": "SURPAYÉ" if ecart > 0 else "SOUS_PAYÉ",
                    "statut_actuel": statut,
                    "montant_ttc": ttc_attendu,
                    "total_regle": total_paye,
                    "ecart": ecart,
                })
            elif statut == "Payée" and total_paye < ttc_attendu:
                anomalies.append({
                    "id_facture": id_f,
                    "type": "STATUT_INCOHERENT",
                    "statut_actuel": statut,
                    "montant_ttc": ttc_attendu,
                    "total_regle": total_paye,
                    "ecart": ecart,
                })

        return {"ok": True, "count": len(anomalies), "anomalies": anomalies}
    except Exception as err:
        return {"ok": False, "message": "API error", "error": _extraire_erreur(err)}


TOOLS = ["analyserReglements", "detecterAnomalies"]

print("\n📌 Tools Analyse Règlements enregistrés :")
for tool in TOOLS:
    print(f"  • {tool}")