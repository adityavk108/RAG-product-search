from typing import List, Dict, Optional
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)


class GraphService:
    """Neo4j-based knowledge graph service for product relationships."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self):
        """Connect to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close the connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def create_product_node(self, product) -> None:
        """Create a product node."""
        with self.driver.session() as session:
            session.run(
                """
                MERGE (p:Product {id: $product_id})
                SET p.name = $name,
                    p.category = $category,
                    p.brand = $brand,
                    p.price = $price,
                    p.rating = $rating,
                    p.description = $description
                """,
                product_id=product.product_id,
                name=product.name,
                category=product.category,
                brand=product.brand,
                price=product.price,
                rating=product.rating,
                description=product.description
            )

    def create_category_node(self, category: str) -> None:
        """Create or update a category node."""
        with self.driver.session() as session:
            session.run(
                """
                MERGE (c:Category {name: $category})
                SET c.product_count = coalesce(c.product_count, 0) + 1
                """,
                category=category
            )

    def create_brand_node(self, brand: str) -> None:
        """Create or update a brand node."""
        with self.driver.session() as session:
            session.run(
                """
                MERGE (b:Brand {name: $brand})
                SET b.product_count = coalesce(b.product_count, 0) + 1
                """,
                brand=brand
            )

    def create_category_relationship(self, product_id: str, category: str) -> None:
        """Create BELONGS_TO relationship."""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (c:Category {name: $category})
                CREATE (p)-[:BELONGS_TO]->(c)
                """,
                product_id=product_id,
                category=category
            )

    def create_brand_relationship(self, product_id: str, brand: str) -> None:
        """Create MANUFACTURED_BY relationship."""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (p:Product {id: $product_id})
                MERGE (b:Brand {name: $brand})
                CREATE (p)-[:MANUFACTURED_BY]->(b)
                """,
                product_id=product_id,
                brand=brand
            )

    def create_similar_relationships(self, product_id: str, similar_ids: List[str], scores: List[float]) -> None:
        """Create SIMILAR_TO relationships."""
        if not similar_ids:
            return

        with self.driver.session() as session:
            session.run(
                """
                MATCH (p:Product {id: $product_id})-[r:SIMILAR_TO]->()
                DELETE r
                """,
                product_id=product_id
            )

            pairs = [{"sim_id": sid, "score": score} for sid, score in zip(similar_ids, scores)]
            session.run(
                """
                UNWIND $pairs AS pair
                MATCH (p:Product {id: $product_id})
                MATCH (s:Product {id: pair.sim_id})
                WHERE p.id <> s.id
                CREATE (p)-[:SIMILAR_TO {score: pair.score}]->(s)
                """,
                product_id=product_id,
                pairs=pairs
            )

    def get_similar_products(self, product_id: str, limit: int = 5) -> List[Dict]:
        """Get similar products from graph."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product {id: $product_id})-[r:SIMILAR_TO]->(s:Product)
                RETURN s.id AS product_id, s.name AS name, r.score AS score
                ORDER BY r.score DESC
                LIMIT $limit
                """,
                product_id=product_id,
                limit=limit
            )
            return [dict(record) for record in result]

    def get_products_by_category(self, category: str, limit: int = 20) -> List[str]:
        """Get products by category."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: $category})
                RETURN p.id AS product_id
                LIMIT $limit
                """,
                category=category,
                limit=limit
            )
            return [record["product_id"] for record in result]

    def get_products_by_brand(self, brand: str, limit: int = 20) -> List[str]:
        """Get products by brand."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product)-[:MANUFACTURED_BY]->(b:Brand {name: $brand})
                RETURN p.id AS product_id
                LIMIT $limit
                """,
                brand=brand,
                limit=limit
            )
            return [record["product_id"] for record in result]

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product {id: $product_id})
                RETURN p.id AS product_id, p.name AS name, p.category AS category,
                       p.brand AS brand, p.price AS price, p.rating AS rating,
                       p.description AS description
                """,
                product_id=product_id
            )
            record = result.single()
            if record:
                return dict(record)
            return None

    def get_all_categories(self) -> List[str]:
        """Get all categories sorted by product count."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Category)
                RETURN c.name AS name
                ORDER BY c.product_count DESC
                """
            )
            return [record["name"] for record in result]

    def get_all_brands(self) -> List[str]:
        """Get all brands sorted by product count."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (b:Brand)
                RETURN b.name AS name
                ORDER BY b.product_count DESC
                """
            )
            return [record["name"] for record in result]

    def clear_graph(self) -> None:
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Graph cleared")

    def build_graph_from_products(self, products: List, similarity_threshold: float = 0.5, top_k: int = 5):
        """Build graph from product list."""
        logger.info(f"Building graph from {len(products)} products...")

        self.clear_graph()

        for i, product in enumerate(products):
            if (i + 1) % 10 == 0:
                logger.info(f"Creating nodes and relationships for product {i+1}/{len(products)}")

            self.create_product_node(product)
            self.create_category_node(product.category)
            self.create_brand_node(product.brand)
            self.create_category_relationship(product.product_id, product.category)
            self.create_brand_relationship(product.product_id, product.brand)

        logger.info("Creating similarity relationships...")
        self._create_all_similarity_relationships(products, similarity_threshold, top_k)

        logger.info("Graph building complete")

    def _create_all_similarity_relationships(self, products: List, threshold: float, top_k: int):
        """Create similarity relationships using embeddings."""
        from app.services.vector_store import vector_store

        if not hasattr(vector_store, 'text_index') or vector_store.text_index is None:
            logger.warning("Vector store not initialized, skipping similarity relationships")
            return

        text_index = vector_store.text_index
        product_ids = vector_store.product_ids

        if text_index.ntotal == 0:
            logger.warning("Empty vector index, skipping similarity relationships")
            return

        embeddings_np = text_index.reconstruct_n(0, text_index.ntotal)

        for i, product_id in enumerate(product_ids):
            query_vec = embeddings_np[i:i+1]
            scores, indices = text_index.search(query_vec, top_k + 1)

            similar_ids = []
            similar_scores = []

            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx != i and idx < len(product_ids):
                    if score >= threshold:
                        similar_ids.append(product_ids[idx])
                        similar_scores.append(float(score))

            if similar_ids:
                self.create_similar_relationships(product_id, similar_ids, similar_scores)

        logger.info("Similarity relationships created")

    def get_graph_stats(self) -> Dict:
        """Get graph statistics."""
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Product)
                    RETURN count(p) AS product_count
                    """
                )
                record = result.single()
                product_count = record["product_count"] if record else 0

                result = session.run(
                    """
                    MATCH (c:Category)
                    RETURN count(c) AS category_count
                    """
                )
                record = result.single()
                category_count = record["category_count"] if record else 0

                result = session.run(
                    """
                    MATCH (b:Brand)
                    RETURN count(b) AS brand_count
                    """
                )
                record = result.single()
                brand_count = record["brand_count"] if record else 0

                result = session.run(
                    """
                    MATCH (p:Product)-[:BELONGS_TO]->(:Category)
                    RETURN count(*) AS category_rels
                    """
                )
                record = result.single()
                category_rels = record["category_rels"] if record else 0

                result = session.run(
                    """
                    MATCH (p:Product)-[:MANUFACTURED_BY]->(:Brand)
                    RETURN count(*) AS brand_rels
                    """
                )
                record = result.single()
                brand_rels = record["brand_rels"] if record else 0

                result = session.run(
                    """
                    MATCH (p:Product)-[:SIMILAR_TO]->(:Product)
                    RETURN count(*) AS similar_rels
                    """
                )
                record = result.single()
                similar_rels = record["similar_rels"] if record else 0

                return {
                    "product_count": product_count,
                    "category_count": category_count,
                    "brand_count": brand_count,
                    "category_rels": category_rels,
                    "brand_rels": brand_rels,
                    "similar_rels": similar_rels
                }
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {}


graph_service = GraphService(
    uri="bolt://neo4j:7687",
    user="neo4j",
    password="password"
)