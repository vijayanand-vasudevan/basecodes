

class iDataHolder
{

public:
using Ptr=std::shared_ptr<iDataHolder>;

virtual ~iDataHolder(){]
}

template <typename T>
class TDataHolder : public iDataHolder
{
	T _data;

	public:
		TDataHolder()
		{}

		TDataHolder(const T& data_)
		:_data(data_)
		{}

		inline T& data() { return _data; }
};

template <typename T>
inline void set(T& t)
{
	_x = iDataHolder::Ptr( new TDataHolder<T>(t) );
}

template <typename T>
T& get()
{
	return dynamic_cast<TDataHolder<T>*>(_x.get())->data();
}

