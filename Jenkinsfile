pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Verify Environment') {
            steps {
                sh '''
                    echo "=== Herramientas disponibles ==="
                    docker --version
                    docker-compose --version
                    echo "=== Estructura del proyecto ==="
                    pwd
                    ls -la
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'docker-compose build --no-cache'
            }
        }

        stage('Start Test Infrastructure') {
            steps {
                sh '''
                    echo "=== Iniciando solo MySQL y Redis para tests ==="
                    docker-compose -f docker-compose.test.yml up -d test-mysql test-redis
                    echo "=== Esperando 45 segundos para inicialización de MySQL ==="
                    sleep 45
                    echo "=== Verificando estado de los servicios ==="
                    docker-compose -f docker-compose.test.yml ps
                    docker-compose -f docker-compose.test.yml logs test-mysql | tail -20
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "=== Ejecutando tests con aplicación ==="
                    docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test-web
                '''
            }
            post {
                always {
                    sh '''
                        echo "=== Limpiando entorno de test ==="
                        docker-compose -f docker-compose.test.yml down
                        docker-compose -f docker-compose.test.yml logs --no-color > test_logs.txt
                        echo "=== Logs de test guardados ==="
                        cat test_logs.txt | tail -50
                    '''
                    archiveArtifacts artifacts: 'test_logs.txt', fingerprint: true
                }
            }
        }

        stage('Deploy to Development') {
            steps {
                sh '''
                    echo "=== Desplegando entorno de desarrollo ==="
                    docker-compose down
                    docker-compose up -d
                    sleep 30
                '''
            }
        }

        stage('Integration Test') {
            steps {
                script {
                    // Aumentado a 3 minutos para dar suficiente tiempo
                    timeout(time: 180, unit: 'SECONDS') {
                        sh '''
                            echo "=== Realizando pruebas de integración ==="
                            
                            # Espera inicial para que la aplicación esté lista
                            sleep 20
                            echo "=== Iniciando verificaciones... ==="
                            
                            # Intentos más eficientes con mejor feedback
                            for i in {1..25}; do
                                echo "🔍 Intento $i/25 - Verificando conectividad..."
                                
                                # Primero probar health check
                                if curl -s -f http://localhost:5000/health > /dev/null; then
                                    echo "✅ Health check exitoso"
                                    
                                    # Luego probar endpoint principal
                                    if curl -s -f http://localhost:5000/login > /dev/null; then
                                        echo "✅ Endpoint /login funcionando"
                                        echo "🎉 INTEGRATION TESTS PASSED - Aplicación completamente operativa"
                                        exit 0
                                    else
                                        echo "⚠️  Health OK pero /login no responde, reintentando..."
                                    fi
                                else
                                    echo "⏳ Aplicación aún no lista, esperando 5s..."
                                fi
                                sleep 5
                            done
                            
                            echo "❌ ERROR: Timeout - La aplicación no respondió correctamente después de 25 intentos"
                            echo "=== Debug information ==="
                            docker-compose ps
                            echo "=== Últimos logs de la aplicación ==="
                            docker-compose logs --tail=30 flask-app
                            exit 1
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
                echo "=== Capturando logs antes de limpiar ==="
                docker-compose logs --tail=30 flask-app
            '''
            sh '''
                echo "=== Limpiando entorno de desarrollo ==="
                docker-compose down
                docker-compose -f docker-compose.test.yml down
                docker system prune -f
            '''
            cleanWs()
        }
        success {
            echo "✅ Pipeline COMPLETADO EXITOSAMENTE"
        }
        failure {
            echo "❌ Pipeline FALLÓ - Revisar logs de test"
            sh '''
                echo "=== Últimos logs de MySQL ==="
                docker-compose -f docker-compose.test.yml logs test-mysql | tail -30
                echo "=== Últimos logs de Test Web ==="  
                docker-compose -f docker-compose.test.yml logs test-web | tail -30
            '''
        }
        aborted {
            echo "⚠️  Pipeline ABORTADO por timeout"
            sh '''
                echo "=== Capturando logs de diagnóstico ==="
                docker-compose ps
                docker-compose logs --tail=50 flask-app
            '''
        }
    }
}
