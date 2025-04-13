import os
from google.cloud import documentai

def perform_ocr_with_document_ai(file_path):
    project_id = 'quick-receipts-450104'
    location = 'us'
    processor_id = 'f9f60237ff49ce2d'

    mime_type = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }.get(os.path.splitext(file_path)[-1].lower())

    if not mime_type:
        raise ValueError("Unsupported file type")

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    resource = client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as f:
        raw_document = documentai.RawDocument(content=f.read(), mime_type=mime_type)

    result = client.process_document(request=documentai.ProcessRequest(name=resource, raw_document=raw_document))
    entities = [ {
        "type": e.type_,
        "text_value": e.text_anchor.content or e.mention_text,
        "normalized_value": getattr(e.normalized_value, 'text', None),
        "confidence": getattr(e, 'confidence', 0.0)
    } for e in result.document.entities ]

    for e in result.document.entities:
        for prop in e.properties:
            entities.append({
                "type": prop.type_,
                "text_value": prop.text_anchor.content or prop.mention_text,
                "normalized_value": getattr(prop.normalized_value, 'text', None),
                "confidence": getattr(prop, 'confidence', 0.0)
            })

    avg_confidence = sum(e['confidence'] for e in entities) / len(entities) if entities else 0.0
    total_amount = next((float(e['normalized_value']) for e in entities if e['type'] == 'total_amount' and e['normalized_value']), None)

    return {
        'ocr_results': entities,
        'avg_confidence': avg_confidence,
        'total_amount': total_amount
    }
