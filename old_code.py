def process_conversations():
    print("Procesando conversaciones...")
    num_cursor = db.get_unprocessed_users()
    for row in num_cursor.fetchall():
        whatsapp_number = row[0]
        print ("Mensajes pendientes de procesar para ", whatsapp_number)
        #Inicializo messsages con con el prompt para la IA pidiendole  uun resumen
        summary_prompt = """Eres un asistente experto en procesar conversaciones. A continuación, recibirás una transcripción completa entre un usuario y un bot. 
        Tu tarea es resumir la conversación, con mucha brevedad incluyendo el nombre del usuario en el caso en que dispongas de él y analizar si el usuario ha reservado una clase de prueba. """         
        messages = [{"role": "system", "content" : summary_prompt }]          
        msg_cursor = db.get_messages_by_user(whatsapp_number)
        for message, sender, timestamp in msg_cursor.fetchall():            
            messages.append({"role": sender, "content": message})
            #print(messages)
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages = messages)
        for choice in response.choices:
            messages.append({"role": "assistant", "content": choice.message.content})
        response_message = response.choices[0].message.content   
        print(response_message, "Número: ", whatsapp_number)
        #Mandamos la respuesta a través de Twilio al telefono del admin
        message = twilio_client.messages.create(
            from_=twilio_number,
            body = response_message,
            to = admin_number
        )
        #Apunto que ya he procesado los mensajes de este usuario
        db.update_processed_messages(whatsapp_number)
        time.sleep(1)
    print("Conversaciones procesadas")

    
    def start_conversations_processing():
    print("Thread for conversation running")
    schedule.every().day.at("11:50").do(process_conversations)
    #schedule.every().minute.at(":23").do(process_conversations)
    while True:
        schedule.run_pending()
        time.sleep(1)      