from traits.api import Property, HasTraits, Float

class TestProp(HasTraits):
	a = Float
	b = Property(depends_on='a')
	c = Property(depends_on='b')
	
	def _get_b(self):
		return self.a * 2
		
	def _get_c(self):
		return self.b * 4
		
tprop = TestProp()
tprop.a = 1.0
print(tprop.c)
tprop.a = 2.0
print(tprop.c)
