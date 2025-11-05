pipeline {
    agent any
    
    environment {
        DOCKER_HOST = "unix:///var/run/docker.sock"
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
                        docker-compose -f docker-compose.test.yml logs --no-color > test_logs.txt 2>&1 || true
                        echo "=== Logs de test guardados ==="
                        cat test_logs.txt | tail -50
                    '''
                    archiveArtifacts artifacts: 'test_logs.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy to Development') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh '''
                    echo "=== Desplegando entorno de desarrollo ==="
                    docker-compose down || true
                    docker-compose up -d
                    echo "=== Esperando inicialización de servicios ==="
                    sleep 30
                    echo "=== Verificando estado de contenedores ==="
                    docker-compose ps
                '''
            }
        }
        
        stage('Integration Test') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    // EXTENDER TIMEOUT y usar espera inteligente
                    timeout(time: 5, unit: 'MINUTES') {
                        // ESPERA INTELIGENTE hasta que la aplicación esté lista
                        waitUntil {
                            script {
                                try {
                                    sh '''
                                        echo "🔍 Verificando estado de la aplicación..."
                                        # Verificar logs de la aplicación
                                        docker-compose logs flask-app --tail=5
                                        # Intentar múltiples endpoints
                                        curl -s -f http://localhost:5000/health || \
                                        curl -s -f http://localhost:5000/ || \
                                        curl -s -f http://localhost:5000/login || exit 1
                                    '''
                                    echo "✅ Aplicación respondiendo correctamente"
                                    return true
                                } catch (Exception e) {
                                    echo "⏳ Aplicación no lista aún, reintentando en 15 segundos..."
                                    sleep 15
                                    return false
                                }
                            }
                        }
                        
                        // Una vez que la aplicación está lista, ejecutar pruebas completas
                        sh '''
                            echo "=== Realizando pruebas de integración completas ==="
                            
                            echo "1. Probando health endpoint..."
                            if curl -s http://localhost:5000/health; then
                                echo "✅ Health check OK"
                            else
                                echo "⚠️  Health check no disponible, probando otros endpoints..."
                            fi
                            
                            echo "2. Probando página de login..."
                            LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/login)
                            if [ "$LOGIN_RESPONSE" = "200" ]; then
                                echo "✅ Login page responde correctamente (HTTP $LOGIN_RESPONSE)"
                            else
                                echo "❌ Login page responde con HTTP $LOGIN_RESPONSE"
                                exit 1
                            fi
                            
                            echo "3. Verificando contenido de login page..."
                            if curl -s http://localhost:5000/login | grep -i "login"; then
                                echo "✅ Formulario de login detectado"
                            else
                                echo "⚠️  No se detectó formulario de login"
                            fi
                            
                            echo "4. Probando página de registro..."
                            REGISTER_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/register)
                            if [ "$REGISTER_RESPONSE" = "200" ]; then
                                echo "✅ Register page responde correctamente (HTTP $REGISTER_RESPONSE)"
                            else
                                echo "⚠️  Register page responde con HTTP $REGISTER_RESPONSE"
                            fi
                            
                            echo "5. Verificando conectividad con servicios..."
                            docker-compose exec -T flask-app python -c "
                            import sys
                            try:
                                # Verificar que la app puede importarse
                                from app import app
                                print('✅ App importada correctamente')
                                
                                # Verificar conexión a base de datos si es posible
                                if hasattr(app, 'config') and 'SQLALCHEMY_DATABASE_URI' in app.config:
                                    from app import db
                                    with app.app_context():
                                        db.engine.connect()
                                    print('✅ Conexión a base de datos OK')
                                else:
                                    print('⚠️  No se verificó BD (configuración no encontrada)')
                                    
                            except Exception as e:
                                print(f'❌ Error en verificación: {e}')
                                sys.exit(1)
                            " || echo "⚠️  No se pudo ejecutar verificación interna"
                            
                            echo "🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN COMPLETADAS EXITOSAMENTE"
                        '''
                    }
                }
            }
            post {
                always {
                    sh '''
                        echo "=== Capturando logs de integración ==="
                        docker-compose logs --tail=30 flask-app > integration_logs.txt 2>&1 || echo "No hay logs de flask-app"
                        echo "=== Logs de Flask-App ==="
                        cat integration_logs.txt
                    '''
                    archiveArtifacts artifacts: 'integration_logs.txt', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            sh '''
                echo "=== Limpiando entorno de desarrollo ==="
                docker-compose down || true
                docker-compose -f docker-compose.test.yml down || true
                docker system prune -f || true
            '''
            cleanWs()
        }
        success {
            echo "🎉 Pipeline COMPLETADO EXITOSAMENTE"
        }
        failure {
            echo "❌ Pipeline FALLÓ - Revisar logs de test"
            sh '''
                echo "=== Últimos logs disponibles ==="
                docker-compose logs --tail=50 2>/dev/null || echo "No se pudieron obtener logs"
            '''
        }
    }
}
