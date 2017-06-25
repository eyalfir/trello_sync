#! groovy
node {
  retry (5) {
    checkout scm
  }
  sh 'env'
  sh 'git clean -fx && rm -rf build/ dist/ venv/'
  stage 'build'
  sh "sed -i.bak 's/BUILD/${env.BUILD_NUMBER}/' setup.py"
  sh 'python setup.py bdist_wheel'
  stage 'deploy'
  sh 'virtualenv venv'
  sh '. venv/bin/activate && pip install dist/trello_sync*whl'
}

