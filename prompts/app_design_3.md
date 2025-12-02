I am writing a simple e-commerce shopping cart/order system in python.
The point of this app is that I am going to refactor it multiple times in order to show how it will look under these different architectures:

- Clean
- Command Query Responsibility Segregation (CQRS)
- Event-driven
- Service-Oriented
- Modular monolith
- Ports and adapters (hexagonal)
- n-tier
- layered
- MVC
- vertical slice
- domain-driven design
- onion
- microservices

I have chosen to implement the following functionality in the app:

- User auth (to show cross-cutting concerns)
- List products
- View product details
- Add item to cart
- Remove item from cart
- Update item quantity in cart
- View cart
- Calculate cart total (with and without shipping and tax)
- Apply discount code
- Place order (checkout)
- Cancel order
- Check/Reserve/Free inventory
- Call payment gateway
- Order lifecycle (order status)
- View order history

Is this sufficient functionality to see meaningful differences between the different architectures?
