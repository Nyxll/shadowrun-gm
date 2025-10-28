@echo off
echo Starting xAI Parser...
echo Output will be saved to parsed-xai-data\parser.log
node tools\process-xai-batch.js > parsed-xai-data\parser.log 2>&1
echo.
echo Done! Check parsed-xai-data\parser.log for details
type parsed-xai-data\parser.log
