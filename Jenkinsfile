pipeline {
    agent any
    
    environment {
        DOCKER_HOST = "unix:///var/run/docker.sock"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/JesusAIM64/Terraform.git'
                sh 'ls -la'
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test-web'
            }
            post {
                always {
                    sh 'docker-compose -f docker-compose.test.yml down'
                }
            }
        }
        
        stage('Deploy to Dev') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d'
                sh 'sleep 10'
            }
        }
        
        stage('Smoke Test') {
            steps {
                sh '''
                    curl -f http://localhost:5000/login || exit 1
                    echo "Smoke test passed - Application is responding"
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose down || true'
            cleanWs()
        }
        success {
            emailext (
                subject: "✅ Pipeline EXITOSO: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "El pipeline se completó exitosamente.\nURL: ${env.BUILD_URL}",
                to: "tu-email@dominio.com"
            )
        }
        failure {
            emailext (
                subject: "❌ Pipeline FALLIDO: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "El pipeline ha fallado. Revisar logs.\nURL: ${env.BUILD_URL}",
                to: "tu-email@dominio.com"
            )
        }
    }
}
