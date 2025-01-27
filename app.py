from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import markdown

app = Flask(__name__)

def convert_markdown_to_html(text):
  
    md = markdown.Markdown(extensions=['extra'])
    
    html = md.convert(text)
    
    return html

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

def gemini_response(prompt):
   
    API_KEY = "AIzaSyCwyjIPRVcDmZJUgt_9vq7WUaqQPSX3TN4"
    genai.configure(api_key=API_KEY)
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    response = model.generate_content(prompt).text
    print(response)
    
    html_response = convert_markdown_to_html(response)
    
    return html_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-medical-form', methods=['POST'])
def submit_medical_form():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'age', 'temperature', 'bloodGroup', 'diseaseDescription']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        try:
            age = int(data['age'])
            temperature = float(data['temperature'])
            
        except ValueError:
            return jsonify({'message': 'Invalid age or temperature format'}), 400
        
        if not (0 <= age <= 150):
            return jsonify({'message': 'Invalid age range'}), 400
        
        if not (95 <= temperature <= 108):
            return jsonify({'message': 'Invalid temperature range'}), 400
        
        prompt = f"""
            Based on your provided information:
            Age: {data['age']} years
            Body Temperature: {data['temperature']}°F
            Blood Group: {data['bloodGroup']}
            Medical Description: {data['diseaseDescription']}

            Please provide a structured analysis in the following format:
            Dear {data['name']},

            This is your medical report,

            **Patient Summary** (limit to 4-5 lines or 50-70 words):
            Summarize the patient's primary symptoms and health concerns concisely.

            **Possible Diagnosis** (limit to 4-5 lines or 50-70 words):
            List the likely conditions in order of probability, starting with the most probable.

            **Recommended Actions**:
                a) **Home Remedies** (if any and safe): List 2-3 suggestions for home care.
                b) **First Aid Measures**: Brief instructions if any immediate actions are required.
                c) **Medical Assistance**: Specify if urgent care is needed and why.

            Please keep the response professional, friendly, and act as if you are a doctor.
        """

        
        ai_response = gemini_response(prompt)
        
        return jsonify({
            'message': 'Form submitted successfully',
            'data': {
                'name': data['name'],
                'age': age,
                'temperature': temperature,
                'bloodGroup': data['bloodGroup'],
                'diseaseDescription': data['diseaseDescription']
            },
            'aiResponse': ai_response
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
