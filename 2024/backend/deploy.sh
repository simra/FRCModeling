# Login to Azure
az login --tenant eb68451c-c266-4fdb-a4fb-bdfe8d631405

# Create a resource group
az group create --name frcBrackets --location "WestUS2"

# Create an App Service plan
az appservice plan create --name frcBrackets --resource-group frcBrackets --sku B1 --is-linux

# Create a web app
az webapp create --resource-group frcBrackets --plan frcBrackets --name frcBrackets --runtime "PYTHON|3.7" --deployment-local-git

# Navigate to your Flask app's directory
rm -rf static/build
cd ../frontend
npm build
cp -a build/. ../backend/static
cd ../backend


# Initialize a local Git repository and commit your code
#git init
#git add .
#git commit -m "Initial commit"

# Add the Azure remote
#git remote add azure <deploymentLocalGitUrl-from-create-step>

# Push your code to Azure
#git push azure master