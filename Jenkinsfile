pipeline {
  agent any
  stages {
    stage('Parsing test') {
      parallel {
        stage('Parsing test') {
          steps {
            sh '''

source ./spins/bin/activate.fish
'''
            sh '''python3 _Parser.py
'''
          }
        }
        stage('') {
          steps {
            sh 'pwd'
          }
        }
      }
    }
    stage('Build succeeded') {
      steps {
        git(url: 'git@github.com:LemurPwned/spintronics-visual.git', changelog: true, branch: 'master', credentialsId: 'LemurPwned')
      }
    }
    stage('End stage') {
      steps {
        echo 'done'
      }
    }
  }
}