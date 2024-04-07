from flask import Flask, render_template, request, send_file
from rdflib import Graph, Namespace
import csv

app = Flask(__name__, static_url_path='/static')


# Load the TTL file into an RDF graph
g = Graph()
g.parse(r"C:\Users\chada\OneDrive\Desktop\web\books_amazon.ttl", format="turtle")

# Define the SPARQL namespace and prefixes
ns = Namespace("http://goodreads.com/resource/")

# Predefined SPARQL queries
queries = {
    "List all books with price < 20$ and whose authors name contains Stephen": """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dbr: <http://goodreads.com/resource/>
        PREFIX dbo: <http://goodreads.com/property/>
        #List all books with price < 20$ and whose authors name contains Stephen
        SELECT DISTINCT ?name ?bookName ?price
        WHERE {
        ?entity rdf::type dbr:author .
        ?entity rdfs::label ?name.
        ?entity dbo:isAuthorOf ?book.
        ?book rdfs::label ?bookName.
        ?book dbo:price ?price.
            filter(?price<"20").
            filter regex(?name,'Stephen').
        }
        order by ?price
        LIMIT 20

    """,
    "List of all books with author names published from 2017 and have ratings above 4.5": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr: <http://goodreads.com/resource/>
        PREFIX dbo: <http://goodreads.com/property/>
        #List of all books with author names published from 2017 and have ratings above 4.5
        SELECT DISTINCT ?name ?authorName ?year ?price ?rating ?reviewCount
        WHERE {
        ?entity rdf::type dbr:book .
        ?entity rdfs::label ?name.
        ?entity dbo:hasAuthor ?author.
        ?author rdfs::label ?authorName.
        ?entity dbo:publishedIn ?year.
        ?entity dbo:price ?price.
        ?entity dbo:reviewCount ?reviewCount.
        ?entity dbo:rating ?rating.
        filter(?year>="2017").
        filter(?rating>="4.5").
        }
        order by ?year ?rating

    """,
    "List the books written by J.K.Rowling and bookname start with harry (Get all Harry potter books by J.K. Rowling)": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr: <http://goodreads.com/resource/>
        PREFIX dbo: <http://goodreads.com/property/>
        #List the books written by J.K.Rowling and bookname start with "harry" (Get all Harry potter books by J.K. Rowling)
        SELECT DISTINCT ?name ?bookName ?rating
        WHERE {
        ?entity rdf::type dbr:author .
        ?entity rdfs::label ?name.
        ?entity dbo:isAuthorOf ?book.
        ?book rdfs::label ?bookName.
        ?book dbo:rating ?rating.
        filter(?name="J.K. Rowling").
        filter regex(?bookName,'^harry','i').
        }
        order by ?rating


    """,
    "Find the author of book Allegiant": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr: <http://goodreads.com/resource/>
        PREFIX dbo: <http://goodreads.com/property/>
        #Find the author of book "Allegiant" 
        SELECT DISTINCT ?name
        WHERE {
        ?entity dbo:isAuthorOf dbr:Allegiant.
        ?entity rdfs::label ?name.
        }

    """,
    "List all authors": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr: <http://goodreads.com/resource/>
        PREFIX dbo: <http://goodreads.com/property/>
        #List all authors
        SELECT DISTINCT ?name
        WHERE {
        ?entity rdf::type dbr:author .
        ?entity rdfs::label ?name.
            
        }
        order by ?name



    """
    # Add more predefined queries as needed
}

def execute_sparql_query(query):
    try:
        # Execute the SPARQL query on the RDF graph
        results = g.query(query)
        
        result_string = ""
        
        # Format the query results as a string
        for row in results.bindings:
            for var_name in row:
                var_value = row[var_name]
                result_string += f"{var_name}: {var_value}\n"
            result_string += "\n"
        
        return result_string
    except Exception as e:
        # Handle any exceptions that occur during query execution
        return f"Error executing SPARQL query: {str(e)}"
@app.route("/view_csv")
def view_csv():
    # Replace 'path_to_your_csv_file.csv' with the actual path to your CSV file
    csv_file_path = r"C:\Users\chada\OneDrive\Desktop\web\static\csvfile.csv"
    csv_data = read_csv(csv_file_path)
    # Send the file as a response
    #return send_file(csv_file_path,as_attachment=False)
    
    return render_template('viewcsv.html', csv_data=csv_data)
def read_csv(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        csv_data = list(csv_reader)
    return csv_data
@app.route("/view_ttl")
def view_ttl():
    # Replace 'path_to_your_csv_file.csv' with the actual path to your CSV file
    ttl_file_path = r"C:\Users\chada\OneDrive\Desktop\web\books_amazon.ttl"
    # Send the file as a response
    return send_file(ttl_file_path,as_attachment=False)
    
@app.route("/about")
def about():
    # Replace 'path_to_your_csv_file.csv' with the actual path to your CSV file
    csv_file_path = r"C:\Users\chada\OneDrive\Desktop\web\static\csvfile.csv"
    # Send the file as a response
    #return send_file(csv_file_path,as_attachment=False)
    return render_template("about.html")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query_name = request.form.get("query")
        query = ""

        if query_name == "other":
            query = request.form.get("custom-query")
        else:
            query = queries.get(query_name)

        if query:
            
            try:
                result = execute_sparql_query(query)
                # Concatenate the query name with the result
                result_string = f"Query: {query_name}\n\nResult:\n{result}"
                return render_template("index.html", queries=queries, result_string=result_string)
            except Exception as e:
                # Handle any errors that occur during query execution
                error_message = f"Error processing query: {str(e)}"
                return render_template("index.html", queries=queries, result_string=error_message)
        else :
            error_message = "please type or select a query"
            return render_template("index.html", queries=queries, result_string=error_message)
            

    return render_template("index.html", queries=queries)

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
"""
other example 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbr: <http://goodreads.com/resource/>
PREFIX dbo: <http://goodreads.com/property/>

#List all authors who wrote Non Fiction
SELECT DISTINCT ?name
WHERE {
   ?entity rdf::type dbr:author .
  ?entity rdfs::label ?name.
    ?entity dbo:isAuthorOf ?book.
  ?book dbo:isCategoryOf dbr:Non_Fiction.
}
order by ?name
LIMIT 20


"""
