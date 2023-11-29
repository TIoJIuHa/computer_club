CREATE OR REPLACE FUNCTION calculate_price_for_computer()
RETURNS TRIGGER AS
$BODY$
DECLARE
   cost_per_hour constant NUMERIC(7,2) := 300.00;
BEGIN
  NEW.price = ROUND((EXTRACT(hours from (NEW.session_end - NEW.session_start)) + EXTRACT(minutes from (NEW.session_end - NEW.session_start)) / 60)* cost_per_hour,2);
  RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER set_order_price
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION calculate_price_for_computer();

CREATE OR REPLACE FUNCTION order_price_with_discount(current_order_id INT)
RETURNS NUMERIC AS
$BODY$
DECLARE
  order_discount NUMERIC;
BEGIN
  order_discount := (SELECT discount FROM category
             WHERE id=(SELECT category_id FROM client
                 WHERE id=(SELECT client_id FROM orders
                      WHERE id=current_order_id)
                )
            )::NUMERIC;
  RETURN ROUND(order_price(current_order_id)*(1-order_discount/100),2);
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION order_price(current_order_id INT)
RETURNS NUMERIC AS
$BODY$
DECLARE
  order_price NUMERIC;
  snacks_cost NUMERIC;
BEGIN
  SELECT price INTO order_price FROM orders WHERE id=current_order_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'order with that id doesn`t exist, id = %', current_order_id
      USING ERRCODE = 'invalid_parameter_value';
  END IF;

  snacks_cost := (SELECT COALESCE(SUM(snack.price * snack_orders.amount), 0)
          FROM snack_orders INNER JOIN snack ON snack_orders.snack_id = snack.id
          WHERE snack_orders.order_id = current_order_id);
  RETURN ROUND(snacks_cost + COALESCE(order_price, 0), 2);
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE update_client_category(current_client_id INT) AS
$BODY$
DECLARE
  money_spent NUMERIC;
  temprow RECORD;
  current_category INT;
  max_category INT;
BEGIN
  money_spent := 0;
  FOR temprow IN
        SELECT id FROM orders
    WHERE client_id=current_client_id
    LOOP
        money_spent := money_spent + order_price(temprow.id);
    END LOOP;

  max_category := (SELECT id FROM category
           WHERE money_required <= money_spent
           ORDER BY money_required DESC
           LIMIT 1);
  current_category := (SELECT category_id FROM client
             WHERE id=current_client_id);
  IF NOT FOUND THEN
    RAISE EXCEPTION 'client with that id doesn`t exist, id = %', current_client_id
      USING ERRCODE = 'invalid_parameter_value';
  END IF;

  IF current_category <> max_category THEN
    UPDATE client
    SET category_id=max_category
    WHERE id=current_client_id;
  END IF;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trigger_update_category_from_order()
RETURNS TRIGGER AS
$BODY$
BEGIN
  CALL update_client_category(NEW.client_id);
  RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_category_order
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_category_from_order();

CREATE OR REPLACE FUNCTION trigger_update_category_from_snacks()
RETURNS TRIGGER AS
$BODY$
DECLARE
  current_client INT;
BEGIN
  SELECT client_id INTO current_client FROM orders WHERE id=NEW.order_id;
  CALL update_client_category(current_client);
  RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_category_snack
    AFTER INSERT ON snack_orders
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_category_from_snacks();