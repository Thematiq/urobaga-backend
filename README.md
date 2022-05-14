
# Urobaga


Communication schema:
 - create room 
   - request
    ```json
    {
      "name": "..."
    }
    ```
   - answer
    ```json
    {
      "token": "..."
    }
    ```
 - join room 
   - request
    ```json
    {
      "name": "..."
    }
    ```
   - answer (to all room members)
    ```json
    [
      {
          "name": "...",
          "is_host": "..."
      }
   ]
    ```
 - update rules
     - request
   ```json
    {
      "height": "...",
      "width": "...",
      "...": "..."
    }
   ```
 - answer (to all room members)
    ```json
    [
      {
      "height": "...",
      "width": "...",
      "...": "..."
      }
   ]
    ```
     
 - leave room
     - request
     ```json 
     ```
   - answer (to all room members)
    ```json
      [
        {
            "name": "...",
            "is_host": "..."
        }
     ]
    ```

 - start game
     - request
     ```json 
     ```
   - answer (to all room members)
    ```json
    {
      "message": "start",
      "timeout": "..." 
    }
    ```
   - confirmation (from all members)
   ```json
    {
      "name": "..." 
    }
    ```

 