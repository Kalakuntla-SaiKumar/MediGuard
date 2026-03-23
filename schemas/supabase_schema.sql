-- MediGuard Database Schema for Supabase (PostgreSQL)
-- Run this in Supabase SQL Editor if auto-migration fails

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(120) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    weight FLOAT,
    blood_group VARCHAR(10),
    phone VARCHAR(20),
    medications VARCHAR(1000),
    
    -- Profile information
    age INTEGER,
    gender VARCHAR(20),
    pregnancy_status VARCHAR(20),
    health_conditions VARCHAR(500),
    allergies VARCHAR(500),
    
    -- Account management
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- OAuth
    google_id VARCHAR(255) UNIQUE,
    google_email VARCHAR(120),
    auth_method VARCHAR(20) DEFAULT 'email',
    
    -- Security questions
    security_question_1 VARCHAR(255),
    security_answer_1 VARCHAR(255),
    security_question_2 VARCHAR(255),
    security_answer_2 VARCHAR(255),
    
    -- Password reset
    reset_token VARCHAR(255) UNIQUE,
    reset_token_expiry TIMESTAMP,
    password_reset_requested_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

-- Assessment History table
CREATE TABLE IF NOT EXISTS assessment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    drug1 VARCHAR(100) NOT NULL,
    drug2 VARCHAR(100) NOT NULL,
    condition VARCHAR(100) NOT NULL,
    
    ddi_risk VARCHAR(20),
    dfi_risk_drug1 VARCHAR(20),
    dfi_risk_drug2 VARCHAR(20),
    dci_risk_drug1 VARCHAR(20),
    dci_risk_drug2 VARCHAR(20),
    overall_risk VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for assessment history
CREATE INDEX IF NOT EXISTS idx_assessment_user_id ON assessment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_assessment_created_at ON assessment_history(created_at);
CREATE INDEX IF NOT EXISTS idx_assessment_drug1 ON assessment_history(drug1);

-- Enable Row Level Security (RLS) for better security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_history ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own data
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- RLS Policy: Users can update their own profile
CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- RLS Policy: Users can see their own assessments
CREATE POLICY "Users can view their own assessments" ON assessment_history
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- RLS Policy: Users can insert their own assessments
CREATE POLICY "Users can insert their own assessments" ON assessment_history
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
