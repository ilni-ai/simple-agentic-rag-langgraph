import { useState, useRef, useEffect } from 'react';
import {
  Container, Row, Col, Form, Button, Spinner, Card, OverlayTrigger, Tooltip
} from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { Lightbulb, Trash } from 'react-bootstrap-icons';  // ✅ Trash icon added

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeFollowUpIndex, setActiveFollowUpIndex] = useState(null);
  const [history, setHistory] = useState([]);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const sessionId = "demo-session";

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  const handleSubmit = async (e, customQuery = null, isFollowUp = false, index = null) => {
    e?.preventDefault?.();
    const userQuery = customQuery || query;
    if (!userQuery.trim()) return;

    setLoading(true);
    if (isFollowUp && index !== null) {
      setActiveFollowUpIndex(index);
    }

    try {
      const res = await fetch('http://localhost:5000/agentic-rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQuery, session_id: sessionId }),
      });

      const data = await res.json();
      const newTurn = {
        userQuery,
        facts: data.facts || [],
        response: data.response || '',
        followUpFacts: [],
        followUpResponse: '',
        suggestedQuestions: data.suggestedQuestions || [],
      };

      if (isFollowUp && index !== null) {
        setHistory(prev =>
          prev.map((turn, i) =>
            i === index
              ? {
                  ...turn,
                  followUpFacts: data.facts || [],
                  followUpResponse: data.response || '',
                  suggestedQuestions: data.suggestedQuestions || [],
                }
              : turn
          )
        );
      } else {
        setHistory(prev => [...prev, newTurn]);
      }

      setQuery('');
      inputRef.current?.focus();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setActiveFollowUpIndex(null);
    }
  };

  // ✅ Clear chat history + session
  const resetChat = async () => {
    setHistory([]);
    setQuery('');
    try {
      await fetch(`http://localhost:5000/reset-session?session_id=${sessionId}`, {
        method: 'DELETE'
      });
    } catch (err) {
      console.error('Failed to reset session:', err);
    }
  };

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col md={{ span: 8, offset: 2 }}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="mb-0">Agentic RAG with LangGraph</h2>
            <Button
              variant="outline-danger"
              size="sm"
              onClick={resetChat}
              disabled={loading}
              title="Reset Chat"
            >
              <Trash /> Reset
            </Button>
          </div>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Ask a question:</Form.Label>
              <Form.Control
                ref={inputRef}
                type="text"
                placeholder="e.g. What is agentic RAG?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
                disabled={loading}
              />
            </Form.Group>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? <Spinner animation="border" size="sm" /> : 'Submit'}
            </Button>
          </Form>
        </Col>
      </Row>

      {history.map((turn, index) => (
        <Row className="mb-4" key={index}>
          <Col md={{ span: 8, offset: 2 }}>
            <Card className="mb-2">
              <Card.Header>User</Card.Header>
              <Card.Body><p>{turn.userQuery}</p></Card.Body>
            </Card>

            <Card className="mb-2">
              <Card.Header>Top Retrieved Facts</Card.Header>
              <Card.Body>
                <ul className="mb-0">
                  {turn.facts.map((fact, idx) => (
                    <li key={idx}>{fact}</li>
                  ))}
                </ul>
              </Card.Body>
            </Card>

            <Card className="mb-2">
              <Card.Header>Gemini Response</Card.Header>
              <Card.Body>
                <ReactMarkdown>{turn.response}</ReactMarkdown>
              </Card.Body>
            </Card>

            {turn.suggestedQuestions?.length > 0 && (
              <>
                <div className="mb-2 d-flex align-items-center gap-2">
                  <Lightbulb className="text-warning" />
                  <strong>Suggested Follow-Ups:</strong>
                </div>
                <div className="mb-3 d-flex flex-wrap gap-2">
                  {turn.suggestedQuestions.map((q, i) => (
                    <OverlayTrigger
                      key={i}
                      placement="top"
                      overlay={<Tooltip>Click to ask this follow-up</Tooltip>}
                    >
                      <Button
                        variant="outline-success"
                        size="sm"
                        disabled={loading}
                        onClick={(e) => handleSubmit(e, q, true, index)}
                      >
                        {loading && activeFollowUpIndex === index ? (
                          <Spinner animation="border" size="sm" />
                        ) : (
                          q
                        )}
                      </Button>
                    </OverlayTrigger>
                  ))}
                </div>
              </>
            )}

            {turn.followUpResponse && (
              <>
                <Card className="mb-2">
                  <Card.Header>Follow-Up Retrieved Facts</Card.Header>
                  <Card.Body>
                    <ul className="mb-0">
                      {turn.followUpFacts.map((fact, idx) => (
                        <li key={idx}>{fact}</li>
                      ))}
                    </ul>
                  </Card.Body>
                </Card>
                <Card>
                  <Card.Header>Follow-Up Response</Card.Header>
                  <Card.Body>
                    <ReactMarkdown>{turn.followUpResponse}</ReactMarkdown>
                  </Card.Body>
                </Card>
              </>
            )}
          </Col>
        </Row>
      ))}

      <div ref={bottomRef} />
    </Container>
  );
}

export default App;
