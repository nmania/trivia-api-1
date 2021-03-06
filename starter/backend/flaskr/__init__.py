import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS
import random
from colorama import Fore , Style
from sqlalchemy import and_
from sqlalchemy.sql import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def paginate_categories(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * CATEGORIES_PER_PAGE
  end = start + CATEGORIES_PER_PAGE
  
  categories = [category.format() for category in selection]
  current_categories = categories[start:end]
  return current_categories

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  configedDB = setup_db(app)
  if not configedDB:
    abort(500)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    try:
      if request.method != 'GET': abort(405)    
      categories = Category.query.order_by(Category.id).all()
        
      current_categories = {cat.id:cat.type for cat in categories}

      return jsonify({
        'success': True,
        'categories': current_categories,
        'total_categories': len(Category.query.all())
      })
    except expression as identifier:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    if request.method != 'GET': abort(405)    
    categories = Category.query.order_by(Category.id).all()
    types = {cat.id:cat.type for cat in categories}
    randomCategory = str( random.randint(1, len(categories)))
    questions = Question.query.order_by(Question.id).all()
    
    ## * - OPTIONAL - RANDOM FUNCTIONALITY FOR QUESTIONS VIEW  - RANDOMIZES QUESTIONS ON REFRESH
    #questions = Question.query.filter(Question.category==randomCategory).order_by(Question.id).all()
    #questions = Question.query.order_by(func.random()).all()
    ## * - - - - - -
    current_questions = paginate_questions(request, questions)
    
    if len(current_questions)==0:
      abort(404)  
    
    for category in categories:
      #print('troubleshoot: ', categories, category.id , ' ', questions[0].category, str (category.id) == str (questions[0].category) ) # !Troubleshooting code
      if str (category.id) == str (questions[0].category):
        currentCategory = category.type 
         
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': types,
      'currentCategory': currentCategory
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    if request.method != 'DELETE': abort(405)    
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
      'success': True,
      'deleted': question_id,
      'questions': current_questions,
      'total_questions': len(Question.query.all())
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    if request.method != 'POST': abort(405)    
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
        
    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      # print(f'{Fore.GREEN} question ', question.category, type(question.difficulty), question.answer, question.question)
      # print(f'{Fore.WHITE}')
      question.insert()
      
      questions = Question.query.order_by(Question.id).all()
      current_questions = [question.format() for question in questions]
      lastIndex = len(current_questions)-1
      return jsonify({
      'success': True,
      'created': question.id,
      'question': current_questions[lastIndex],
      'total_questions': len(Question.query.all())
      })
    except:
      abort(422)

 ## ! ---------- OPTIONAL CREATE CATAGORY METHOD ----------DON'T TOUCH

  # @app.route('/categories', methods=['POST'])
  # def create_categories():
  #   body = request.get_json()
  #   new_type = body.get('type', None)
  #   try:
  #     category = Category(type = new_type)
     
  #     category.insert()
      
  #     categories = Category.query.order_by(Category.id).all()
  #     current_categories = {cat.id:cat.type for cat in categories}

  #     return jsonify({
  #     'success': True,
  #     'created': category.id,
  #     'categories': current_categories,
  #     'total_categories': len(Category.query.all())
  #     })
  #   except:
  #     abort(422) 
 
      
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  
  @app.route('/questions/search', methods=['POST'])
  def retrieve_searched_based_questions():
    if request.method != 'POST': abort(405)    
    try:
      body = request.get_json()
      search = body.get('searchTerm', None)
      selection = Question.query.filter(Question.question.ilike('%{}%'.format(search)))
      current_questions = paginate_questions(request, selection)
      
      if (len(selection.all()) !=0 and len(current_questions) == 0):
        abort(404) 
      
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection.all()),
        'current_category': None 
      })
    except:
      abort(422)
    
    
  # done so with last end point - can be done also by creating an endpoint with a search term string passed in the url
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #could also write this in the first questions get endpoint as a JSON body or as a Args request
  @app.route('/categories/<string:category_id>/questions', methods=['GET'])
  def retrieve_category_based_questions(category_id):
    if request.method != 'GET': abort(405)
    
    #category_id= int(category_id)+1
    selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()     
    
    if not len(selection): 
      print(len(selection))
      abort(422)
    
    current_questions = paginate_questions(request, selection)
    
    if len(current_questions) == 0:
      abort(404)  
      
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'current_category': selection[0].category
    })
    

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/questions/quiz', methods=['POST'])
  def retrieve_quiz_questions():
    
    if request.method != 'POST': abort(405)

    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    category= body.get('quiz_category' , {"type": "click", "id" : 0})
    #print('PQ: ', previous_questions, 'C: ', category) #! Troubleshooting code
    

    if category["id"] == 0:
      questions = Question.query.filter(Question.id.notin_(q for q in previous_questions)).order_by(func.random()).all()
    else: 
      questions = Question.query.filter(and_(Question.category == category["id"], Question.id.notin_(q for q in previous_questions))).order_by(func.random()).all()
    
    if len(questions) == 0: 
      question = 0
    if len(questions) == 0 and len(previous_questions) == 0:
      abort(422)
    if len(questions):
      #print('questions before format: ' , questions, 'length of questions: ', len(questions)) #! Troubleshooting code
      question = questions[0].format()
      #print('length of question', len(question), ' question contents: ' , question, ' question ID: ' , question['id']) #! Troubleshooting code
      previous_questions.append(question['id'])
      
    return jsonify({
      'success': True,
      'question': question,
      'previous_questions':previous_questions,
      'total_questions': len(questions)
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource or url not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
    
  @app.errorhandler(405)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  return app

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Something is wrong with the server configuration"
      }), 500
  return app

    