# KaybolanDiller API Documentation

## Overview

The KaybolanDiller API provides endpoints for translating between rare and endangered languages, with a special focus on Turkish and Turkic dialects. The API is built using FastAPI and supports various language pairs.

## Base URL

```
https://api.kaybolandiller.com/v1
```

## Authentication

All API requests require an API key to be included in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Translate Text

Translates text between supported language pairs.

```http
POST /translate
```

#### Request Body

```json
{
    "source_text": "string",
    "source_language": "string",
    "target_language": "string",
    "model": "string (optional)"
}
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| source_text | string | Text to be translated |
| source_language | string | Source language code (e.g., "tr", "en", "ain") |
| target_language | string | Target language code |
| model | string | Optional: Specific model to use for translation |

#### Response

```json
{
    "translated_text": "string",
    "source_language": "string",
    "target_language": "string",
    "model_used": "string",
    "confidence_score": float
}
```

### List Supported Languages

Returns a list of all supported languages and their codes.

```http
GET /languages
```

#### Response

```json
{
    "languages": [
        {
            "code": "string",
            "name": "string",
            "family": "string",
            "is_endangered": boolean
        }
    ]
}
```

### Get Translation Models

Returns available translation models for a specific language pair.

```http
GET /models/{source_language}/{target_language}
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| source_language | string | Source language code |
| target_language | string | Target language code |

#### Response

```json
{
    "models": [
        {
            "id": "string",
            "name": "string",
            "description": "string",
            "performance_metrics": {
                "bleu_score": float,
                "accuracy": float
            }
        }
    ]
}
```

## Error Responses

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": object
    }
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limits

- Free tier: 100 requests per hour
- Pro tier: 1000 requests per hour
- Enterprise tier: Custom limits

## Language Codes

| Language | Code |
|----------|------|
| Turkish | tr |
| English | en |
| Ainu | ain |
| Meskhetian | mes |
| Karamanlı | kar |
| Gagauz | gag |
| Uyghur | uig |
| Chuvash | chv |
| Kazakh | kaz |
| Bashkir | bak |
| Crimean Tatar | crh |

## Examples

### Translate Text

```bash
curl -X POST "https://api.kaybolandiller.com/v1/translate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "source_text": "Merhaba dünya",
           "source_language": "tr",
           "target_language": "en"
         }'
```

### List Languages

```bash
curl -X GET "https://api.kaybolandiller.com/v1/languages" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

## SDK Support

The API is supported by the following official SDKs:

- Python: `pip install kaybolandiller`
- JavaScript/TypeScript: `npm install @kaybolandiller/api`
- Go: `go get github.com/kaybolandiller/api-go`

## Support

For API support, please contact:
- Email: api@kaybolandiller.com
- GitHub Issues: [https://github.com/makalin/KaybolanDiller/issues](https://github.com/makalin/KaybolanDiller/issues) 