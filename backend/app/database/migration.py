import psycopg2
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv("d:/Khoj_hack/Khoj/backend/.env")

def run_migrations():
    host = "aws-0-ap-southeast-2.pooler.supabase.com"
    port = "6543"
    user = "postgres.sfoevwxxmanqklbslfwe"
    dbname = "postgres"
    password = "Hackathon#1245"
    
    print(f"Connecting to database to execute schema DDL...")
    
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            dbname=dbname,
            password=password,
            connect_timeout=15
        )
        conn.autocommit = False
        cur = conn.cursor()
        
        # 1. Enable uuid extension if needed
        print("Enabling UUID extension...")
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        
        # 2. Create tables
        print("Creating table: cases...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived')),
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        print("Creating table: sources...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                case_id UUID REFERENCES cases(id) ON DELETE CASCADE NOT NULL,
                title TEXT,
                url TEXT,
                source_name TEXT,
                published_at TEXT,
                content TEXT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        print("Creating table: evidence...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                case_id UUID REFERENCES cases(id) ON DELETE CASCADE NOT NULL,
                claim TEXT NOT NULL,
                source TEXT,
                confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
                evidence_type TEXT CHECK (evidence_type IN ('eyewitness', 'official_statement', 'media_report', 'forensic', 'unknown')),
                reasoning TEXT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        print("Creating table: timeline_events...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                case_id UUID REFERENCES cases(id) ON DELETE CASCADE NOT NULL,
                time TEXT NOT NULL,
                event TEXT NOT NULL,
                confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
                supporting_evidence TEXT[],
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        print("Creating table: theories...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS theories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                case_id UUID REFERENCES cases(id) ON DELETE CASCADE NOT NULL,
                theory TEXT NOT NULL,
                confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
                supporting_evidence TEXT[],
                timeline_events TEXT[],
                summary TEXT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        print("Creating table: simulations...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                case_id UUID REFERENCES cases(id) ON DELETE CASCADE NOT NULL,
                theory_id UUID REFERENCES theories(id) ON DELETE SET NULL,
                instructions JSONB,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        
        # 3. Setup Row Level Security
        print("Configuring Row Level Security (RLS)...")
        cur.execute("ALTER TABLE cases ENABLE ROW LEVEL SECURITY;")
        cur.execute("ALTER TABLE sources ENABLE ROW LEVEL SECURITY;")
        cur.execute("ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;")
        cur.execute("ALTER TABLE timeline_events ENABLE ROW LEVEL SECURITY;")
        cur.execute("ALTER TABLE theories ENABLE ROW LEVEL SECURITY;")
        cur.execute("ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;")
        
        # Clean up existing policies to support idempotency
        cur.execute("DROP POLICY IF EXISTS \"Users can manage their own cases\" ON cases;")
        cur.execute("DROP POLICY IF EXISTS \"Users can manage sources of their own cases\" ON sources;")
        cur.execute("DROP POLICY IF EXISTS \"Users can manage evidence of their own cases\" ON evidence;")
        cur.execute("DROP POLICY IF EXISTS \"Users can manage timeline events of their own cases\" ON timeline_events;")
        cur.execute("DROP POLICY IF EXISTS \"Users can manage theories of their own cases\" ON theories;")
        cur.execute("DROP POLICY IF EXISTS \"Users can manage simulations of their own cases\" ON simulations;")
        
        # Create security policies
        print("Applying policies...")
        cur.execute("""
            CREATE POLICY "Users can manage their own cases" ON cases
                FOR ALL TO authenticated
                USING (auth.uid() = user_id)
                WITH CHECK (auth.uid() = user_id);
        """)
        
        cur.execute("""
            CREATE POLICY "Users can manage sources of their own cases" ON sources
                FOR ALL TO authenticated
                USING (EXISTS (SELECT 1 FROM cases WHERE cases.id = sources.case_id AND cases.user_id = auth.uid()))
                WITH CHECK (EXISTS (SELECT 1 FROM cases WHERE cases.id = sources.case_id AND cases.user_id = auth.uid()));
        """)
        
        cur.execute("""
            CREATE POLICY "Users can manage evidence of their own cases" ON evidence
                FOR ALL TO authenticated
                USING (EXISTS (SELECT 1 FROM cases WHERE cases.id = evidence.case_id AND cases.user_id = auth.uid()))
                WITH CHECK (EXISTS (SELECT 1 FROM cases WHERE cases.id = evidence.case_id AND cases.user_id = auth.uid()));
        """)
        
        cur.execute("""
            CREATE POLICY "Users can manage timeline events of their own cases" ON timeline_events
                FOR ALL TO authenticated
                USING (EXISTS (SELECT 1 FROM cases WHERE cases.id = timeline_events.case_id AND cases.user_id = auth.uid()))
                WITH CHECK (EXISTS (SELECT 1 FROM cases WHERE cases.id = timeline_events.case_id AND cases.user_id = auth.uid()));
        """)
        
        cur.execute("""
            CREATE POLICY "Users can manage theories of their own cases" ON theories
                FOR ALL TO authenticated
                USING (EXISTS (SELECT 1 FROM cases WHERE cases.id = theories.case_id AND cases.user_id = auth.uid()))
                WITH CHECK (EXISTS (SELECT 1 FROM cases WHERE cases.id = theories.case_id AND cases.user_id = auth.uid()));
        """)
        
        cur.execute("""
            CREATE POLICY "Users can manage simulations of their own cases" ON simulations
                FOR ALL TO authenticated
                USING (EXISTS (SELECT 1 FROM cases WHERE cases.id = simulations.case_id AND cases.user_id = auth.uid()))
                WITH CHECK (EXISTS (SELECT 1 FROM cases WHERE cases.id = simulations.case_id AND cases.user_id = auth.uid()));
        """)
        
        conn.commit()
        print("MIGRATIONS COMPLETED SUCCESSFULLY!")
        
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        print("MIGRATION FAILED:", e)
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migrations()
