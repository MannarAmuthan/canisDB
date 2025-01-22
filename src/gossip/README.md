
### canisDB gossip protocol

#### Message
```json
{
  "type": "internal",
  "prop": {
    "request": "state_check"
  }
}

```

#### Response

```json
{
  "type": "internal",
  "prop": {
    "response": "ready" // ready, not_ready
  }
}

```



      