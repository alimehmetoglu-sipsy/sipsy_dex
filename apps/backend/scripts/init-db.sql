-- PostgreSQL Database Initialization Script for DexAgents
-- This script is executed when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS dexagents;

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create schema if needed (optional, using public schema by default)
-- CREATE SCHEMA IF NOT EXISTS dexagents;

-- Set search path
-- SET search_path TO dexagents, public;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'DexAgents PostgreSQL database initialized successfully';
END $$;